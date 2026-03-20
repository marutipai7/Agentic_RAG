from django.urls import path
from rag.api import views

urlpatterns = [
    # Pages
    path('',                views.login_view,         name='login'),
    path('register/',       views.register_view,      name='register'),
    path('logout/',         views.logout_view,         name='logout'),
    path('dashboard/',      views.dashboard_view,      name='dashboard'),
    path('chat/',           views.ragchat_view,        name='chat'),
    path('profile/',        views.profile_view,        name='profile'),
    path('upload-view/',    views.upload_view,         name='upload-view'),
    path('vector-store/',   views.vector_store_view,   name='vector-store'),
    path('llm-stats/',      views.llm_stats_view,      name='llm-stats'),
    path('forgot-password/',views.forgot_password_view,name='forgot-password'),
    path('reset-password/<uuid:token>/', views.reset_password_view, name='reset-password'),

    # Chat APIs
    path('chat/new/',       views.new_chat_view,       name='new-chat'),
    path('chat/history/',   views.chat_history_view,   name='chat-history'),
    path('chat/clear/',     views.clear_chat_queue_view,name='clear-chat'),
    path('query/',          views.QueryAPIView.as_view(),name='query'),

    # Vector store APIs
    path('upload/',         views.UploadDocumentView.as_view(),  name='upload-document'),
    path('chunks/',         views.CheckChunkView.as_view(),      name='check-chunks'),
    path('search/',         views.SimilaritySearchView.as_view(),name='similarity-search'),
    path('chunks/edit/',                    views.edit_chunk_view,         name='edit-chunk'),
    path('vectorstore/purge/',              views.purge_vector_store_view, name='purge-vectorstore'),
    path('documents/delete/<str:doc_id>/',  views.delete_document_view,    name='delete-document'),
    path('chunks/delete/<str:chunk_id>/',   views.delete_chunk_view,       name='delete-chunk'),
]