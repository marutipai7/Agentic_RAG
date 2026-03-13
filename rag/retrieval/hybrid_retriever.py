from rag.vectorstore.chroma_store import ChromaStore
from rag.retrieval.bm25_index import BM25Index
from rag.ingestion.embedding_service import EmbeddingService
from rag.core.dependencies import embedding_function,vector_store

class HybridRetriever:

    def __init__(self):
        embedding = embedding_function

        self.vector_db = vector_store
        self.bm25 = BM25Index()

    def search(self, query, k=5):
        vector_results = self.vector_db.similarity_search(query, k=k)
        bm25_results = self.bm25.searchg(query, k=k)

        results = []

        for doc, score in vector_results:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": float(score),
                "bm25_score": 0
            })
        
        for r in bm25_results:
            results.append({
                "content": r["content"],
                "vector_score": 0,
                "bm25_score": r["bm25_score"]
            })

        