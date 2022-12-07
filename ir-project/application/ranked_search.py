from text_processing import tokenize_text
from tf_idf import tf_idf

# ranked search
def ranked_search(query,k=10):
    """Run ranked query search using tf-idf model.

    Parameters:
    query: user query
    k (int): number of results to return

    Returns:
    Top-k names of books that matchs the query.

   """ 
    tf_idf_result = tf_idf()

    tokens = tokenize_text(query)
    print(tokens)
    query_weights = {}

    for key,value in tf_idf_result.items():
        query_weights[key[1]] = 0 # inicializar tudo com zero

    for key,value in tf_idf_result.items(): # key = (term, doc) value = tfidf 
        if key[0] in tokens: # if term with calculated tf_idf  is equal to query token -> add value
            #print('key[0] in tokens: ',key[0])
            #print('tf_idf_result[key] = ',tf_idf_result[key])
            query_weights[key[1]] = query_weights[key[1]] + tf_idf_result.get(key)

    #print(query_weights)
    query_weights = sorted(query_weights.items(), key=lambda x: x[1], reverse=True) # sort weights in descending order

    return query_weights # return the first k results

