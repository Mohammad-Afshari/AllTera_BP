import re
from collections import Counter, defaultdict
class subwordTokenizer:
    def __init__(self, regex_rule=None , special_tokens=None, basic_tokens=None):
        self.special_tokens = special_tokens or ['<BOS>', '<EOS>', '<UNK>', '<PAD>', '</w>']
        self.basic_tokens = basic_tokens or list('abcdefghijklmnopqrstuvwxyz123456789.,!?;:-()[]{}+/\\@#$%^&*')
        self.regex_rule = regex_rule or re.compile(r'[^a-z123456789\.,!\?;:\-\(\)\[\]\{\}\+\/\\@#\$%\^&\*]+')

        # r'[^a-z0-9><./,:-]+'

        self.freq_vocab= None
        self.merge_rules = None
        self.token_to_id = None
        self.id_to_token = None


    # ---------------------------------------------------

    def normalize(self, text):
        text = text.lower()

        text = text.replace('[inst]', ' <inst> ').replace('[/inst]', ' </inst> ')
        
        self.regex_rule.sub('', text)
        # text = re.sub(self.regex_rule, ' ', text)
        text = re.sub(r'\s+', ' ', text)

        return text.strip()
    
    # ---------------------------------------------------

    def create_freq_vocab(self, text):
        text = self.normalize(text)
        texts = text.split()
        words = []
        for word in texts:
            words.extend(word.split())

        word_freq = Counter(words)

        freq_vocab = {}
        for word, freq in word_freq.items():

            if word.startswith('<') and word.endswith('>'):
                freq_vocab[(word,)] = freq

            else:
                chars = list(word)
                chars.append('</w>')
        
        
                freq_vocab[tuple(chars)] = freq
        self.freq_vocab= freq_vocab
    
    # ---------------------------------------------------
    
    def get_pairs_freq(self):
        pairs = defaultdict(int)

        for word, freq in self.freq_vocab.items():
            symbols = word
            for i in range(len(symbols)-1):
                pairs[symbols[i], symbols[i+1]] += freq

        return pairs

    def merge_vocab(self, pair,):
        new_vocab = {}
        bigram = ''.join(pair)

        for word, freq in self.freq_vocab.items():
            w = list(word)

            i = 0
            new_word = []

            while i < len(w):
                if i < len(w)-1 and (w[i], w[i+1]) == pair:
                    new_word.append(bigram)
                    i+=2
                else:
                    new_word.append(w[i])
                    i+=1

            new_vocab[tuple(new_word)] = freq

        return new_vocab

    # ---------------------------------------------------

    def create_merge_rules(self, num_merges):
        merge_rules = []
        for i in range(num_merges):

            # just for dv
            # dv -> developer experience XD
            if (i+1)%200 == 0:
                print(f'Merging... {i+1}/{num_merges}')

            pairs = self.get_pairs_freq()
            if not pairs:
                break
            best = max(pairs, key=pairs.get)
            self.freq_vocab= self.merge_vocab(best)
            merge_rules.append(best)
        self.merge_rules = merge_rules

    # ---------------------------------------------------
    
    def text_to_token(self, word):

        if word.startswith('<') and word.endswith('>'):
            return [word]
    
        word = self.normalize(word)

        toks = list(word)
        toks.append('</w>')

        i = 0

        for pair in self.merge_rules:
            i = 0
            while i < len(toks)-1:
                if (toks[i], toks[i+1]) == pair:
                    toks[i:i+2] = [''.join(pair)]
                else:
                    i+=1
        return toks

    # ---------------------------------------------------

    def buid_vocab(self):
        vocab = []
        vocab.extend(self.special_tokens)
        vocab.extend(self.basic_tokens)

        for pair in self.merge_rules:
            vocab.append(''.join(pair))

        token_to_id = {}
        id_to_token = {}
        for id, tok in enumerate(vocab):
            token_to_id[tok] = id
            id_to_token[id] = tok

        self.token_to_id , self.id_to_token = token_to_id, id_to_token

    # ---------------------------------------------------

    def create_new_tokenizer(self, text_to_fit, num_merge_rules):
        self.create_freq_vocab(text_to_fit)
        self.create_merge_rules(num_merge_rules)
        self.buid_vocab()


    def tokenize_text(self, text):
        words = text.split()
        tokens_ids = []

        for word in words:
            tokens = self.text_to_token(word)
            for token in tokens:
                if token not in self.token_to_id:
                    tokens_ids.append(self.token_to_id['<UNK>'])

                else:
                    tokens_ids.append(self.token_to_id[token])

        return tokens_ids
    
    # GOT SOME ISSUES! NOT COMPLETE!!!
    def create_training_data_from_text(self, trainig_text, seq_length):

        # WORKING ON:
        # trainig_text = trainig_text.split()
        # new = []
        # for word in trainig_text:
        #     if word not in list('.,!?;:-()[]{}+/\\@#$%^&* '):
        #         new.append(word+'</w>')
        # trainig_text = ' '.join(new)

        trainig_text = self.normalize(trainig_text)
        tokenized_training_text = self.text_to_token(trainig_text)
        
        sequences = []
        
        for bos_word_index in range(len(tokenized_training_text)):
            if bos_word_index > len(tokenized_training_text) - seq_length*3:
                return sequences
            else:
                seq = []
                seq.append(self.token_to_id['<BOS>'])

                for i in range(seq_length-1):
                    
                    # sequence beggining index(bos_word_index) + token of sequence index(i)

                    if tokenized_training_text[bos_word_index + i] in self.token_to_id:
                        seq.append(self.token_to_id[tokenized_training_text[bos_word_index+i]])

                    else:
                        seq.append(self.token_to_id['<UNK>'])
                
                    if len(seq) == seq_length:
                        seq.append(self.token_to_id['<EOS>'])
                        sequences.append(seq)
                        break


        return sequences

toknizer = subwordTokenizer()
full_text = open('dataset.txt').read(100000)
toknizer.create_new_tokenizer(full_text,5000)

trtxt = ''
seqs = toknizer.create_training_data_from_text(trtxt,5)
for seq in seqs:
    print(seq)
    txxt = []
    for tok in seq:
        txxt.append(toknizer.id_to_token[tok])
    print(' '.join(txxt))