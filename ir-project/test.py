# imports
import re
import unicodedata
import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.tokenize import sent_tokenize , word_tokenize
from collections import Counter
nltk.download('punkt')
nltk.download('stopwords')

WORD_MIN_LENGTH = 2 ## we'll drop all tokens with less than this size


# get data
import boto3

s3 = boto3.client('s3') # com as variaveis de ambiente configuradas, a boto3 ja procura suas credenciais para iniciar uma sessao 
s3 = boto3.resource('s3')

bucket = s3.Bucket('comprehend-processed-output') # bucket de escolha. nesse caso, onde chegam os arquivos txt com o resumo

corpus = {} # dict com key = titulo e value = texto
array_of_docs = [] # array com textos
string_of_docs = ""
# criei essas duas formas porque assim a gente vê qual é mais útil

print('Loop to insert every document in corpus array')
count_docs = 0
for object in bucket.objects.all(): # objects.all() fornece uma lista, que contem todos os objetos do bucket
    s3BucketName = object.bucket_name
    s3ObjectKey = object.key
    # https://stackoverflow.com/questions/31976273/open-s3-object-as-a-string-with-boto3
    s3ObjectContent = object.get()['Body'].read().decode('utf-8') 
    count_docs = count_docs+1
    print(s3BucketName)
    print(count_docs,' - ',s3ObjectKey) # nome do arquivo
    #print(s3ObjectContent)
    corpus[s3ObjectKey] = s3ObjectContent
    array_of_docs.append(s3ObjectContent)
    string_of_docs = string_of_docs + s3ObjectContent
    

print('num of docs: ',len(corpus.keys()))
# process text

STOP_WORDS = set(stopwords.words('portuguese'))
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
    """Make all necessary preprocessing of text: 
    strip accents and punctuation, 
    remove \n, t
    okenize our text, 
    convert to lower case, remove stop words and 
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

files_with_tokens = {}

# loop to tokenize each document

for video_title,transcription_summary in corpus.items():
   
    text = transcription_summary
    #Clean and Tokenize text of each document
    words = tokenize_text(text)
    print('tokenized text')
    #print(words)
    #Store tokens
    files_with_tokens[video_title] = words


inverted_index = {} # token, list of docs it occurs, occurance freq in each doc 
                                                     # tf(t,d)
tf_aux = {}

# count token frequency in a file
print('tf aux, freq of term in a file')
for file,tokens in files_with_tokens.items(): # for each file and its list of words
    # count each token frequency
    tcount = Counter(tokens) # tcount is a dic {token: frequency}
    print(tcount)
    for term,freq in tcount.items():
        print(term,freq)
        key = (term,file)
        tf_aux[key] = freq # store term frequency in the file
print(tf_aux)

print('list_of_doc_occurance, list of documents a term occur on')
# for each term, list of doc it occurs
list_of_doc_occurance = {}
terms_list = tokenize_text(string_of_docs) # make a list with all the corpus
terms_list = list(set(terms_list)) # remover repetidos

for term in terms_list:
    list_of_doc_occurance[term] = []
    for file_name, terms in files_with_tokens.items():
        if term in terms:   
            list_of_doc_occurance[term].append(file_name)

print(list_of_doc_occurance)
#tokenized_corpus = tokenize_text(string_of_docs)
#print(tokenized_corpus)

# tf: tf(t,d) = num occurances of t in d / total tokens in d
print('tf')
tf = {}
for key,value in tf_aux.items(): # key eh uma tupla ne, ver linha 114  term, file
    freq = value
    #print(value)
    #print(key[0],key[1])
    # key de tf tbm vai ser tupla (term,file)
    tf[key] = freq/ len(files_with_tokens[key[1]]) # files_with_tokens[key[1] = video title
    #print(key[0],',',key[1],' : ', tf[key])
# idf: idf(t,c) = number of docs in corpus  / (1 + num of docs in which t appears)
                  # len(corpus.keys())
print('idf')
idf = {}
corpus_size = len(corpus.keys())
for term,files in list_of_doc_occurance.items():
    print(term)
    print(len(files))
for term, files in list_of_doc_occurance.items():
    idf[term] = corpus_size/(1+len(files))
    print('idf of ', term,': ',idf[term])

# tf*idf
tf_idf = {}

# initiate array, all 0
for key, value in tf.items(): # key is a tuple (term, doc) and value is the tf
    tf_idf[key] = 0

for key, value in tf.items(): # key is a tuple (term, doc) and value is the tf
    
    tf_idf[key] += tf[key]*idf[key[0]] # sum tfidf for each tf tuple of a term
    print('tfidf of ',key[0],' in doc ', key[1],': ',tf_idf[key])

"""
print('******TF******')
print(tf)
print('******IDF******')
print(idf)
print('******TF IDF******')
print(tf_idf)
"""

# ranked search
def ranked_search(k, tf_idf, query):
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
    for key,value in tf_idf.items():
        query_weights[key[1]] = 0

    for key,value in tf_idf.items():
        if key[0] in tokens: # se termo da query = token  no vetor de tf idf
            query_weights[key[1]] += tf_idf[key]
    
    query_weights = sorted(query_weights.items(), key=lambda x: x[1], reverse=True)

    return query_weights[:k]
    
"""
result = ranked_search(10,tf_idf,'cientista brasileiro')
print('RESULTADO DA QUERY')
print(result)
print('MELHOR NOTA:')
print(result[0])
print('doc com maior nota e seu conteudo: ',result[0][0])
print(corpus[result[0][0]])

"""

# cosine similarity