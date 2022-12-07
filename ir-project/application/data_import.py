# get data
import boto3

s3 = boto3.client('s3') # com as variaveis de ambiente configuradas, a boto3 ja procura suas credenciais para iniciar uma sessao 
s3 = boto3.resource('s3')
bucket = s3.Bucket('comprehend-processed-output') # bucket de escolha. nesse caso, onde chegam os arquivos txt com o resumo

corpus = {} # dict com key = titulo e value = texto
array_of_docs = [] # array com textos
string_of_docs = ""
# criei essas duas formas porque assim a gente vê qual é mais útil

print('data_import\nLoop to insert every document in corpus array')
count_docs = 0
for object in bucket.objects.all(): # objects.all() fornece uma lista, que contem todos os objetos do bucket
    s3BucketName = object.bucket_name
    s3ObjectKey = object.key
    # https://stackoverflow.com/questions/31976273/open-s3-object-as-a-string-with-boto3
    s3ObjectContent = object.get()['Body'].read().decode('utf-8') 
    count_docs = count_docs+1
    #print(s3BucketName)
    #print(count_docs,' - ',s3ObjectKey) # nome do arquivo
    #print(s3ObjectContent)
    corpus[s3ObjectKey] = s3ObjectContent
    array_of_docs.append(s3ObjectContent)
    string_of_docs = string_of_docs + s3ObjectContent

print('Data imported')
def get_corpus():
    return corpus

def get_array_of_docs():
    return array_of_docs

def get_string_of_docs():
    return string_of_docs

def get_file_content(file_name):
    return corpus[file_name]
