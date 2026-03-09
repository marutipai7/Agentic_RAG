from rag.ingestion.embedding_service import EmbeddingService
from rag.vectorstore.chroma_store import ChromaStore
from rag.services.retrival_services import RetrievalService
from rag.services.ingestion_services import IngestionService

embedding_service = EmbeddingService()
embedding_function = embedding_service.get_embeddings()

vector_store = ChromaStore(embedding_function)

ingestion_service = IngestionService(vector_store)
retrieval_service = RetrievalService(vector_store)