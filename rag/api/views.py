from django.shortcuts import render
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from rag.services.ingestion_services import IngestionService
from rag.ingestion.embedding_service import EmbeddingService
from rag.vectorstore.chroma_store import ChromaStore
from rag.services.retrival_services import RetrievalService

from rag.core.dependencies import ingestion_service, retrieval_service, vector_store
# Create your views here.


class UploadDocumentView(APIView):

    parser_class  = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')

        file_path = f"uploads/{file.name}"

        with open(file_path, 'wb+') as f:
            for chunk in file.chunks():
                f.write(chunk)

        result = ingestion_service.ingest_pdf(file_path)

        return Response(result, status=status.HTTP_200_OK)
    
class CheckChunkView(APIView):
    def get(self, request):
        data = vector_store.get_all_chunks()

        return Response({
            "status": "success",
            "total_chunks": len(data["documents"]),
            "documents": data["documents"][:10]
        })
    
class SimilaritySearchView(APIView):
    def get(self, request):
        query = request.GET.get("query", "")
        k = int(request.GET.get("k", 5))

        if not query:
            return Response({
                "status": "error",
                "message": "Query parameter is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        result = retrieval_service.search(query, k=k)

        return Response(result)