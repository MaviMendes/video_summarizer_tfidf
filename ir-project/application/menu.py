from ranked_search import ranked_search
from data_import import get_corpus, get_file_content

class menu:
    def __init__(self) -> None:
        pass
    def get_menu_options(self):
        menu = "HELLO!\nChoose an option:\n1-query\n2-read a file\n3-list files\n4-exit"
        print(menu)
        option = input()
        self.execute_option(option)

        menu2 = "Want to do something else?\n5-yes\n6-no"
        print(menu2)
        option = input()
        self.execute_option(option)
    
    def query(self):
        user_query = input("Input query:  ")
        result = ranked_search(user_query)

        for item in result:
            print('Document: ',item[0])
            print('Relevance: ',item[1])
        

    def read_file(self):
        file_of_interest = input('Input file name:  ')
        print(get_file_content(file_of_interest))

    def list_files(self):
        print('LIST OF FILES')
        corpus = get_corpus()
        for file, content in corpus.items():
            print(file)
        
    def execute_option(self,option):
        
        if(option == '1'):
            self.query()

        if(option == '2'):
            self.read_file()

        if(option == '3'):
            self.list_files()

        if(option == '4'):
            exit()

        if(option == '5'):
            self.get_menu_options()

        if(option == '6'):
            exit()
        
