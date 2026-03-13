from rag.ingestion.document_loader import DocumentLoader
from rag.ingestion.text_splitter import TextSplitter
from rag.ingestion.embedding_service import EmbeddingService
from rag.vectorstore.chroma_store import ChromaStore
from rag.retrieval.bm25_index import BM25Index
from langchain_community.vectorstores.utils import filter_complex_metadata

class IngestionService:

    def __init__(self, vector_store):
        ## Store in vector DB
        self.vector_store = vector_store
    def ingest_pdf(self, file_path):
        # load documents
        documents = DocumentLoader.load_pdf(file_path)

        # chunk documents
        chunks = TextSplitter.split_documents(documents)
        chunks = filter_complex_metadata(chunks)
        bm25 = BM25Index()
        bm25.add_documents(chunks)
        # add chunks to vector store
        self.vector_store.add_documents(chunks)

        return {
            "status": "success",
            "message": f"Document '{file_path}' ingested successfully.",
            "chunks_added": len(chunks)
        }