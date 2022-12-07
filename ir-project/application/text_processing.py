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
STOP_WORDS = set(stopwords.words('portuguese'))

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