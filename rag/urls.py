
from django.urls import path, include
from rag.api import views
urlpatterns = [
    path("upload/", views.UploadDocumentView.as_view(), name="upload-document"),
    path("chunks/", views.CheckChunkView.as_view(), name="check-chunks"),
    path("search/", views.SimilaritySearchView.as_view(), name="similarity-search")
]