# Application to query S3 data using TF-IDF

This application is a project to a university class, Introduction do Textual Information Processing

### test.py
Contains all the application, so to say<br>
My first draft

### getS3Objects.py

Program I made to test getting data from s3<br>
I am using environment variables to start the session, therefore I can share the code without sharing my keys

### vector_model.py

The first test with the vector model I made. It is based on a medium and a kaggle blog, which are very informative<br>
1- https://towardsdatascience.com/tf-idf-for-document-ranking-from-scratch-in-python-on-real-world-dataset-796d339a4089 <br>
2- https://www.kaggle.com/code/vabatista/introduction-to-information-retrieval/notebook

## application
This folder contains the aimed application. There is plenty of space for improvement, I will probably continue changing this one<br>

### data_import.py

Gets data from s3 and stores in data structures<br>
Functions returning this data structures so other programs can use them<br>

### main.py

Calls the menu to start the application interaction with the user

### menu.py

Have functions to interact with the user and call the modules responsible for retrieving the query result

### ranked_search.py

Builds a data structure containing the documents and its relevance considering the given query<br>
Uses tf_idf values 

### tf_idf.py

Functions calculating tf,idf and tf_idf

### text_processing.py

Functions to tokenize the text, remove punctuation, put in lowercase, etc

## Next steps

Currently, I get the data from s3, txt files containing summary of videos<br>
The workflow is working with step functions and lambda, and Amazon Transcribe and Amazon Comprehend do the IA part of the job<br>
A next step will be try to replace transcribe and comprehend with my own algorithm and use them as a source of comparison<br>
Also, the search method can be improved<br>
A friendly interface is also intended<br>
The final step will be deploying everything as a web application<br>
