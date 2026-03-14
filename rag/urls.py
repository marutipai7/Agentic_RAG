
from django.urls import path, include
from rag.api import views
urlpatterns = [
    path("", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("profile/", views.profile_view, name="profile"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("chat/", views.ragchat_view, name="chat"),
    path("vector-store/", views.vector_store_view, name="vector-store"),
    path("upload-view/", views.upload_view, name="upload"),
    path("llm-stats/", views.llm_stats_view, name="llm-stats"),


    path("upload/", views.UploadDocumentView.as_view(), name="upload-document"),
    path("chunks/", views.CheckChunkView.as_view(), name="check-chunks"),
    path("search/", views.SimilaritySearchView.as_view(), name="similarity-search"),
    path("query/", views.QueryAPIView.as_view(), name="query"),
]