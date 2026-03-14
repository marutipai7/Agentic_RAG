from langchain_chroma import Chroma

class ChromaStore:
    def __init__(self, embedding_function):
        self.db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

    def add_documents(self, documents):
        self.db.add_documents(documents)
        self.db.persist()               ## safe to remove

    def get_store(self):
        return self.db

    def similarity_search(self, query, k=5):
        results = self.db.similarity_search(query, k=k)
        return results
    
    def similarity_search_with_score(self, query, k=5):
        results = self.db.similarity_search_with_score(query, k=k)
        return results

    def get_all_chunks(self):
        return self.db.get()
    