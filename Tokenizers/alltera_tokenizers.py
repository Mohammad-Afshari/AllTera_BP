import re
from collections import Counter, defaultdict
class subwordTokenizer:
    def __init__(self, regex_rule=None , special_tokens=None, basic_tokens=None):
        self.special_tokens = special_tokens or ['<PAD>', '<inst>', '</inst>', '<UNK>', '</w>']
        self.basic_tokens = basic_tokens or list('abcdefghijklmnopqrstuvwxyz123456789.,!?;:-()[]{}+/\\@#$%^&*<>')
        self.regex_rule = regex_rule or re.compile(r'[^a-z123456789\!\?\.\,><]+')
        # self.regex_rule = regex_rule or re.compile(r'[^a-z123456789\.,!\?;\:\-\(\)\[\]\{\}\+\/\\@#\$%\^&\*><]+')
        # r'[^a-z0-9><./,:-]+'


        self.freq_vocab= None
        self.merge_rules = None
        self.token_to_id = None
        self.id_to_token = None

    # ---------------------------------------------------

    def normalize(self, text):
        text = text.lower()
        text = text.replace('[inst]', '<inst>').replace('[/inst]', '</inst>')
        text = re.sub(self.regex_rule, ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    # ---------------------------------------------------

    def create_freq_vocab(self, text):
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
    
    # ---------------------------------------------------
    
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
    
    def text_to_tokens(self, text:str):
        # word to tokens
        text_list = text.split()

        if len(text_list) == 1:
            word = text

            # if it's special token
            if word.startswith('<') and word.endswith('>'):
                # WARNING: Do not change this line to << return [word] >> !
                return word
            
            # word = self.normalize(word)
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
            # return ''.join(toks)
            return toks
        
        # sentences to tokens
        else:
            text_tokens = []

            for word in text_list:
                # if it's special token
                if word.startswith('<') and word.endswith('>'):
                    text_tokens.append(word)

                else:
                    # word = self.normalize(word)
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
                    # text_tokens.append(''.join(toks))
                    text_tokens.extend(toks)


            return text_tokens
        
    # ---------------------------------------------------

    def text_to_token_ids(self, text):

        # word to ids
        if len(text.split()) == 1:
            token_ids = []
            tokens = self.text_to_tokens(text)

            # WARNING: Do not use << if len(tokens) == 1 >> in next line of Code !
            # Because if the text is a word, len will count word length and code will not work proper.
            # If the text is word, self.text_to_tokens() output will be string, not list.
            # We'll use this feature as a flag for seperating words and sentences.
            # if type(tokens) == str:
            #     token = tokens
            #     if token not in self.token_to_id:
            #         token_ids.append(self.token_to_id['<UNK>'])
            #     else:
            #         token_ids.append(self.token_to_id[token])

            # return token_ids

            if type(tokens) == str:
                # special token
                token = tokens
                return [ self.token_to_id.get(token, self.token_to_id['<UNK>']) ]
            else:
                # tokens is list of subword pieces
                return [ self.token_to_id.get(tok, self.token_to_id['<UNK>']) for tok in tokens ]



        # sentences to ids
        else: 
            # words = text.split()
            # token_ids = []

            # for word in words:
            #     tokens = self.text_to_token_ids(word)
            #     for token in tokens:
            #         if token not in self.token_to_id:
            #             token_ids.append(self.token_to_id['<UNK>'])

            #         else:
            #             token_ids.append(self.token_to_id[token])

            # return token_ids
            words = text.split()
            token_ids = []

            for word in words:
                sub_tokens = self.text_to_token_ids(word)
                token_ids.extend(sub_tokens)

            return token_ids

    
    # ---------------------------------------------------

    def detokenize_array(self, id_array):
        text = ""
        for id in id_array:
            token = self.id_to_token[id]
            text += token.replace('</w>',' ')
        return text

    # ---------------------------------------------------

    def create_training_data_from_text(self, training_text, seq_length):
        tokenized_training_text = self.text_to_tokens(training_text)
        
        sequences = []
        
        for bos_word_index in range(len(tokenized_training_text)):
            # Defines a boundary to stop creating:
            if bos_word_index > len(tokenized_training_text) - seq_length*2:
                break
            else:
                seq = []
                # seq.append(self.token_to_id['<BOS>'])
                for i in range(seq_length):
                    # Sequence beggining index(bos_word_index) + sequence token index(i)
                    if tokenized_training_text[bos_word_index + i] in self.token_to_id:
                        seq.append(self.token_to_id[tokenized_training_text[bos_word_index+i]])

                    else:
                        seq.append(self.token_to_id['<UNK>'])
                
                    if len(seq) == seq_length:
                        # seq.append(self.token_to_id['<EOS>'])
                        sequences.append(seq)
                        break
        # return sequences

        input_seq = []
        target_seq = []

        for i in range(len(sequences)):
            if i+1 < len(sequences):
                input_seq.append(sequences[i])
                target_seq.append(sequences[i+1])

        return input_seq, target_seq

    # ---------------------------------------------------

    def create_new_tokenizer(self, text_to_fit, num_merge_rules):
        self.create_freq_vocab(text_to_fit)
        self.create_merge_rules(num_merge_rules)
        self.buid_vocab()

    # ---------------------------------------------------

    def save_tokenizer_configs(self, path):
        # configs = {
        #     "special_tokens" : self.special_tokens,
        #     "basic_tokens" : self.basic_tokens,
        #     # "regex_rule" : self.regex_rule,
        #     "merge_rules" : self.merge_rules,
        #     "token_to_id" : self.token_to_id,
        #     "id_to_token" : self.id_to_token
        # }

        # import json
        # # json_str = json.dumps(configs, indent=4)
        # # with open(f"{path_to_save}/tokenizer_configs.json", "w") as f:
        # #     f.write(json_str)
        # with open(f"{path_to_save}/tokenizer_configs.json", 'w') as f:
        #     f.write(json.dumps(configs, ensure_ascii=False, indent=4))

        import json

        configs = {
            "special_tokens": self.special_tokens,
            "basic_tokens": self.basic_tokens,
            "merge_rules": [list(pair) for pair in self.merge_rules],   # convert tuple -> list
            "token_to_id": self.token_to_id,
            "id_to_token": {str(k): v for k, v in self.id_to_token.items()},  # convert keys -> string
            "regex_rule": self.regex_rule.pattern
        }

        with open(f"{path}/tokenizer_configs.json", 'w', encoding='utf-8') as f:
            json.dump(configs, f, ensure_ascii=False, indent=4)


    # ---------------------------------------------------

    def load_tokenizer_configs(self, config_file_path):
        # import json
        # json_str = open(config_file_path).read()
        # configs = json.loads(json_str)

        # self.special_tokens = configs["special_tokens"]
        # self.basic_tokens = configs["basic_tokens"]
        # # self.regex_rule = configs["regex_rule"]
        # self.merge_rules = configs["merge_rules"]
        # self.token_to_id = configs["token_to_id"]
        # self.id_to_token = configs["id_to_token"]

        import json
        with open(config_file_path, 'r', encoding='utf-8') as f:
            configs = json.load(f)

        self.special_tokens = configs["special_tokens"]
        self.basic_tokens = configs["basic_tokens"]

        # convert lists → tuples
        self.merge_rules = [tuple(pair) for pair in configs["merge_rules"]]

        # restore int keys
        self.id_to_token = {int(k): v for k, v in configs["id_to_token"].items()}
        self.token_to_id = configs["token_to_id"]

        # restore regex
        import re
        self.regex_rule = re.compile(configs["regex_rule"])


tokenizer = subwordTokenizer()
dataset_file = open('/home/mohammad/Desktop/Datasets/dataset.txt')
dataset_text = tokenizer.normalize(dataset_file.read())

tokenizer.create_new_tokenizer(dataset_text,15000)
tokenizer.save_tokenizer_configs('/home/mohammad/Desktop/Projects/AllTera Build Projekt/Tokenizers')

# tokenizer.load_tokenizer_configs('/home/mohammad/Desktop/Projects/AllTera Build Projekt/Tokenizers/tokenizer_configs.json')


training_text = tokenizer.normalize(dataset_file.read(10000))
inpu, targ = tokenizer.create_training_data_from_text(training_text, 20)

for i in range(len(inpu)):
    print(f'inpu: {inpu[i]}')

    text_tokens = []
    for token in inpu[i]:
        text_tokens.append(tokenizer.id_to_token[token])
    
    text = ''
    for text_token in text_tokens:
        text += text_token.replace('</w>',' ').replace('<UNK>',' <UNK> ')#.replace('<inst>',' :QUESTION').replace('</inst>',' :ANSWER')
    print(text)

    print(f'targ: {targ[i]}')

    text_tokens = []
    for token in targ[i]:
        text_tokens.append(tokenizer.id_to_token[token])
    
    text = ''
    for text_token in text_tokens:
        text += text_token.replace('</w>',' ').replace('<UNK>',' <UNK> ')#.replace('<inst>',' :QUESTION').replace('</inst>',' :ANSWER')
    print(text)