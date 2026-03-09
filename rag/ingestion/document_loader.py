from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader, UnstructuredPowerPointLoader

class DocumentLoader:

    @staticmethod
    def load_pdf(file_path):
        loader =PyPDFLoader(file_path)
        documents = loader.load()
        return documents
    
    @staticmethod
    def load_test(file_path):
        loader = TextLoader(file_path)
        documents = loader.load()
        return documents
    
