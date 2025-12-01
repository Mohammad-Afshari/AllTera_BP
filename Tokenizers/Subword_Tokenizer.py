import re
from tkinter import filedialog 
from collections import Counter, defaultdict
special_tokens = ['<BOS>', '<EOS>', '<UNK>', '<PAD>', '</w>']
basic_tokens = list('abcdefghijklmnopqrstuvwxyz123456789')

f_path = filedialog.askopenfile(title="Select text file.").name
f = open(f_path)
full_text = f.read(500000)

def normalize(text):
    text = text.lower()

    text = text.replace('[inst]', ' <inst> ').replace('[/inst]', ' </inst> ')
    text = re.sub('[^a-z0-9<->/]+', ' ', text)

    text = re.sub(r'\s+', ' ', text)

    return text.strip()

def create_freq_vocab(text):
    texts = full_text.split()
    words = []
    for word in texts:
        word = normalize(word)
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
    return freq_vocab

def get_pairs_freq(freq_vocab):
    pairs = defaultdict(int)

    for word, freq in freq_vocab.items():
        symbols = word
        for i in range(len(symbols)-1):
            pairs[symbols[i], symbols[i+1]] += freq

    return pairs

def merge_vocab(pair, freq_vocab):
    new_vocab = {}
    bigram = ''.join(pair)

    for word, freq in freq_vocab.items():
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

def create_merge_rules(num_merges, freq_vocab):
    merge_rules = []
    for i in range(num_merges):
        pairs = get_pairs_freq(freq_vocab)
        if not pairs:
            break
        best = max(pairs, key=pairs.get)
        freq_vocab = merge_vocab(best, freq_vocab)
        merge_rules.append(best)

        if i%200 == 0:
            print(f'Merging... {i}/{num_merges}')
    return merge_rules

def word_to_token(word, merge_rules):

    if word.startswith('<') and word.endswith('>'):
        return [word]
    
    word = normalize(word)

    symbols = list(word)
    symbols.append('</w>')

    i = 0

    for pair in merge_rules:
        i = 0
        while i < len(symbols)-1:
            if (symbols[i], symbols[i+1]) == pair:
                symbols[i:i+2] = [''.join(pair)]
            else:
                i+=1
    return symbols


def buid_vocab(merge_rules):
    vocab = []
    vocab.extend(special_tokens)
    vocab.extend(basic_tokens)

    for pair in merge_rules:
        vocab.append(''.join(pair))

    token_to_id = {}
    id_to_token = {}
    for id, tok in enumerate(vocab):
        token_to_id[tok] = id
        id_to_token[id] = tok

    return token_to_id, id_to_token

def tokenize_text(text, merge_rules, token_to_id):
    words = text.split(' ')
    tokens_ids = []

    for word in words:
        word = normalize(word)

        tokens = word_to_token(word, merge_rules)
        for token in tokens:
            if token not in token_to_id:
                tokens_ids.append(token_to_id['<UNK>'])
            else:
                tokens_ids.append(token_to_id[token])
    return tokens_ids


freq_vocab = create_freq_vocab(full_text)
merge_rules = create_merge_rules(5000, freq_vocab)
tok2id, id2tok = buid_vocab(merge_rules)

# See an example of breaking text using merge rules
# print(encode_word('hello there i am mohammad',merge_rules))

# See an example of tokenizing
example_tokenized = tokenize_text('Hello there my name is mohammad. I love nlp and AI!', merge_rules, tok2id)
print(example_tokenized)