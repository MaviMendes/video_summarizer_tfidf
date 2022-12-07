from collections import Counter
from text_processing import tokenize_text
from data_import import get_corpus, get_string_of_docs


def tokenized_corpus():

    #print('tokenize_corpus')
    tokenized_corpus = {}

    # loop to tokenize each document
    corpus = get_corpus()

    for video_title,transcription_summary in corpus.items():
    
        text = transcription_summary
        #Clean and Tokenize text of each document
        words = tokenize_text(text)
        #print('tokenized text')
        #print(words)
        #Store tokens
        tokenized_corpus[video_title] = words

    return tokenized_corpus



def tf_aux():
    tf_aux = {}

    # count token frequency in a file
    #print('tf aux, freq of term in a file')
    for file,tokens in tokenized_corpus().items(): 
        tcount = Counter(tokens) 
        for term,freq in tcount.items():
            key = (term,file)
            tf_aux[key] = 0 
            
    for file,tokens in tokenized_corpus().items(): # for each file and its list of words
        # count each token frequency
        tcount = Counter(tokens) # tcount is a dic {token: frequency}
        #print(tcount)
        for term,freq in tcount.items():
            #print(term,freq)
            key = (term,file)
            tf_aux[key] += freq # store term frequency in the file

    return tf_aux

def list_of_doc_occurance():
    #print('list_of_doc_occurance, list of documents a term occur on')
    # for each term, list of doc it occurs -> useful in idf calculation
    list_of_doc_occurance = {}
    terms_list = tokenize_text(get_string_of_docs()) # make a list with all the corpus
    terms_list = list(set(terms_list)) # remover repetidos

    for term in terms_list:
        list_of_doc_occurance[term] = []
        for file_name, terms in tokenized_corpus().items():
            if term in terms:   
                list_of_doc_occurance[term].append(file_name)

    return list_of_doc_occurance

def tf():
    # tf: tf(t,d) = num occurances of t in d / total tokens in d
    print('tf')
    tf = {}
    tokenized_corpus_result = tokenized_corpus()
    for key,value in tf_aux().items(): # key eh uma tupla ne, ver linha 114  term, file
        freq = value
        #print(value)
        #print(key[0],key[1])
        # key de tf tbm vai ser tupla (term,file)
        tf[key] = freq/ len(tokenized_corpus_result[key[1]]) # files_with_tokens[key[1] = video title
        #print(key[0],',',key[1],' : ', tf[key])

    return tf

# idf: idf(t,c) = number of docs in corpus  / (1 + num of docs in which t appears)
                # len(corpus.keys())
def idf():
    print('idf')
    idf = {}
    corpus_size = len(get_corpus().keys())
    #for term,files in list_of_doc_occurance().items():
        #print(term)
        #print(len(files))
    list_of_doc_occurance_result = list_of_doc_occurance()
    for term, files in list_of_doc_occurance_result.items():
        idf[term] = corpus_size/(1+len(files))
        #print('idf of ', term,': ',idf[term])
    return idf

def tf_idf():
    print('tf_idf')
    # tf*idf
    tf_idf = {}

    tf_result = tf()
    idf_result = idf()

    # initiate array, all 0
    for key, value in tf_result.items(): # key is a tuple (term, doc) and value is the tf
        tf_idf[key] = 0

    for key, value in tf_result.items(): # key is a tuple (term, doc) and value is the tf
        
        tf_idf[key] += tf_result[key]*idf_result[key[0]] # sum tfidf for each tf tuple of a term
        #print('tfidf of ',key[0],' in doc ', key[1],': ',tf_idf[key])

    return tf_idf


#print('Debugging, printing things: ')
#print(tokenized_corpus())
#print(tf_aux())
#print(list_of_doc_occurance())
#print(tf())
#print(idf())
#print(tf_idf())