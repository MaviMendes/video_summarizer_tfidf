# codigo usado no colab, fazer mudancas pra rodar no pc

# ----- get files e importacoes
## Library imports
import numpy as np 
import pandas as pd
import nltk
nltk.download('punkt')
from sklearn.feature_extraction.text import CountVectorizer

import os, glob, re, sys, random, unicodedata, collections
from tqdm import tqdm
from functools import reduce
import nltk
from collections import Counter
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.tokenize import sent_tokenize , word_tokenize
import boto3

session = boto3.Session(aws_access_key_id='AKIA2NHNUTQVFRB2NJWK',aws_secret_access_key='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')

# s3 = session.client('s3') # com as variaveis de ambiente configuradas, a boto3 ja procura suas credenciais para iniciar uma sessao 
s3 = session.resource('s3')
bucket = s3.Bucket('comprehend-processed-output') # bucket de escolha. nesse caso, onde chegam os arquivos txt com o resumo

corpus = {} # dict com key = titulo e value = texto
array_of_docs = [] # array com textos
# criei essas duas formas porque assim a gente vê qual é mais útil

print('Loop to insert every document in corpus array')
for object in bucket.objects.all(): # objects.all() fornece uma lista, que contem todos os objetos do bucket
    s3BucketName = object.bucket_name
    s3ObjectKey = object.key
    # https://stackoverflow.com/questions/31976273/open-s3-object-as-a-string-with-boto3
    s3ObjectContent = object.get()['Body'].read().decode('utf-8') 
    print(s3BucketName)
    print(s3ObjectKey) # nome do arquivo
    #print(s3ObjectContent)
    corpus[s3ObjectKey] = s3ObjectContent
    array_of_docs.append(s3ObjectContent)

STOP_WORDS = set(stopwords.words('portuguese'))

# ------ funcoes de processamento

WORD_MIN_LENGTH = 2 ## we'll drop all tokens with less than this size

def strip_accents(text):
    """Strip accents and punctuation from text. 
    For instance: strip_accents("João e Maria, não entrem!") 
    will return "Joao e Maria  nao entrem "

    Parameters:
    text (str): Input text

    Returns:
    str: text without accents and punctuation

   """    
    nfkd = unicodedata.normalize('NFKD', text)
    newText = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    return re.sub('[^a-zA-Z0-9 \\\']', ' ', newText)

def tokenize_text(text):
    """Make all necessary preprocessing of text: strip accents and punctuation, 
    remove \n, tokenize our text, convert to lower case, remove stop words and 
    words with less than 3 chars.

    Parameters:
    text (str): Input text

    Returns:
    str: cleaned tokenized text

   """        
    text = strip_accents(text)
    text = re.sub(re.compile('\n'),' ',text)
    words = word_tokenize(text)
    words = [word.lower() for word in words]
    words = [word for word in words if word not in STOP_WORDS and len(word) > WORD_MIN_LENGTH]
    return words



def inverted_index(words):
    """Create a inverted index of words (tokens or terms) from a list of terms

    Parameters:
    words (list of str): tokenized document text

    Returns:
    Inverted index of document (dict)

   """       
    inverted = {}
    for index, word in enumerate(words):
        locations = inverted.setdefault(word, [])
        locations.append(index)
    return inverted

def inverted_index_add(inverted, doc_id, doc_index):
    """Insert document id into Inverted Index

    Parameters:
    inverted (dict): Inverted Index
    doc_id (int): Id of document been added
    doc_index (dict): Inverted Index of a specific document.

    Returns:
    Inverted index of document (dict)

   """        
    for word in doc_index.keys():
        locations = doc_index[word]
        indices = inverted.setdefault(word, {})
        indices[doc_id] = locations
    return inverted


inverted_doc_indexes = {}
files_with_index = []
files_with_tokens = {}
doc_id=0


for video_title,transcription_summary in corpus.items():
   
    text = transcription_summary
    #Clean and Tokenize text of each document
    words = tokenize_text(text)
    #Store tokens
    files_with_tokens[video_title] = words

    doc_index = inverted_index(words) # Create a inverted index of words (tokens or terms) from a list of terms
    inverted_index_add(inverted_doc_indexes, doc_id, doc_index) # Insert document id into Inverted Index
    files_with_index.append(video_title) # MUDAR ISSO AQUI
    

print('doc_index: ',doc_index)
# ----- tf idf


## Number of documents each term occurs
DF = {}
print('inverted_doc_indexes: ' , inverted_doc_indexes)
for word in inverted_doc_indexes.keys():
    DF[word] = len ([doc for doc in inverted_doc_indexes[word]])
    print('DF[word]: ', DF[word])

print('DF:',DF)

total_vocab_size = len(DF) # acho q ta errado, seria a soma de cada DF[word]
print('total vocab size: ',total_vocab_size)



tf_idf = {} # Our data structure to store Tf-Idf weights

N = len(files_with_tokens)
print('N = files with tokens: ',N)

for doc_id, tokens in tqdm(files_with_tokens.items()): #tqdm adds timebar to iteration
    
    counter = Counter(tokens)
    words_count = len(tokens)

    print('calculating td_idf, token = ' , token)
    
    for token in np.unique(tokens):
        
        # Calculate Tf
        tf = counter[token] # Counter returns a tuple with each terms counts
        print('tf = counter[token] ', tf)
        tf = 1+np.log(tf)
        print('tf = 1+np.log(tf) ', tf)
        
        # Calculate Idf
        if token in DF:
            df = DF[token]
            print('df = ',df)
        else:
            df = 0
        idf = np.log((N+1)/(df+1))
        print('idf = ',idf)
        
        # Calculate Tf-idf        
        tf_idf[doc_id, token] = tf*idf
        print('doc id:',doc_id)
        print('token: ',token)
        print('tf_idf[doc_id, token] = tf*idf ',tf_idf[doc_id, token])

# ------ parte da pesquisa/query



def ranked_search(k, tf_idf_index, file_names, query):
    """Run ranked query search using tf-idf model.

    Parameters:
    k (int): number of results to return
    tf_idf_index (dict): Data Structure storing Tf-Idf weights to each 
                        pair of (term,doc_id) 
    file_names (list): List with names of files (books)
    query (txt): Query text

    Returns:
    Top-k names of books that matchs the query.

   """   
    tokens = tokenize_text(query)
    query_weights = {}
    for doc_id, token in tf_idf:
        
        if token in tokens: # se termo da query = token  no vetor de tf idf
            query_weights[doc_id] = query_weights.get(doc_id, 0) + tf_idf_index[doc_id, token]
    
    query_weights = sorted(query_weights.items(), key=lambda x: x[1], reverse=True)
    """
    results = []
    print(query_weights)
    
    for doc, weight in query_weights.items():
        results.append(doc) ## retornara uma lista de documentos em ordem

    return results
    """
    return query_weights


# ------ query de teste

test_1 = ranked_search(10, tf_idf, files_with_index,"Johanna Dobereiner")

for doc, weight in test_1:
    print("Doc: ",doc," | Weight: ", weight)

test_2 = ranked_search(10, tf_idf, files_with_index, "plantas")
for doc, weight in test_2:
    print("Doc: ",doc," | Weight: ", weight)
