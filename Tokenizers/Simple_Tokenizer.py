# This Line added to test git!

def normalize(text):
    text = text.lower()
    
    return text

def build_vocab(texts):
    vocab = ['<BOS>', '<EOS>', '<UNK>', '<PAD>']
    
    for text in texts:
        text = normalize(text)

        words = text.split(' ')

        for word in words:
            if word not in vocab:
                vocab.append(word)
    
    token_to_id = {} # hello:1
    id_to_token = {} # 1:hello

    for id, tok in enumerate(vocab):
        token_to_id[tok] = id
        id_to_token[id] = tok

    return token_to_id, id_to_token

def convert_text_to_ids(text, token_to_id, max_len):
    text = normalize(text)
    words = text.split(' ')

    # شروع توالی با
    ids = [token_to_id['<BOS>']]

    for word in words:
        if word in token_to_id:
            ids.append(token_to_id[word])
        else:
            ids.append(token_to_id['<UNK>'])
    
    if len(ids)+1 == max_len:
        ids.append(token_to_id['<EOS>'])
        return ids
    
    elif len(ids) > max_len:
        while len(ids)+1 > max_len:
            ids.pop()
        ids.append(token_to_id['<EOS>'])
        return ids
    
    elif len(ids) < max_len:
        while len(ids)+1 < max_len:
            ids.append(token_to_id['<PAD>'])
        ids.append(token_to_id['<EOS>'])
        return ids
    
def convert_ids_to_text(ids, id_to_token):
    words = []
    for id in ids:
        words.append(id_to_token[id])

    return " ".join(words)


# test
texts = [
    'i love coding so much',
    'i like npl coding',
    'coding and love',
    'hello my name is mohammad'
]

t2i, i2t = build_vocab(texts)