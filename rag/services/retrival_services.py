import time
from rag.ingestion.embedding_service import EmbeddingService
from rag.vectorstore.chroma_store import ChromaStore

class RetrievalService:

    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    def search(self, query, k=5):
        start_time = time.time()

        results = self.vector_store.similarity_search(query, k=k)

        response = []

        for doc, score in results:
            response.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": float(score)
            })
        end_time = time.time()

        return {
            "query": query,
            "top_k": k,
            "results": response,
            "retrieval_time_seconds": end_time - start_time
        }