import json
import time
from datetime import timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg, Sum, Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as drf_status

from rag.core.dependencies import ingestion_service, retrieval_service, vector_store
from rag.models import ChatSession, ChatMessage, LLMCallLog, UserProfile, PasswordResetToken
from rag.services.llm_service import LLMService
from rag.services.agentic_service import AgenticService

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")
        return render(request, "login.html", {"error": "Invalid username or password."})
    return render(request, "login.html")

def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        if password1 != password2:
            return render(request, "register.html", {"error": "Passwords do not match."})
        if len(password1) < 8:
            return render(request, "register.html", {"error": "Password must be at least 8 characters."})
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already taken.'})
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already registered.'})

        user = User.objects.create_user(username=username, 
                                        email=email, 
                                        first_name=first_name, 
                                        last_name=last_name, 
                                        password=password1)
        UserProfile.objects.create(user=user)
        login(request, user)
        return redirect("login")

    return render(request, "register.html")

def logout_view(request):
    logout(request)
    return redirect("login")

def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            token_obj = PasswordResetToken.objects.create(user=user)
            reset_url = f"{request.scheme}://{request.get_host()}/reset-password/{token_obj.token}"

            send_mail(
                subject = "Reset your AgenticRAG password",
                message = f"Click the link below to reset your password: {reset_url}",
                from_email = "noreply@agenticrag.com",
                recipient_list = [email],
                fail_silently=True,
            )
        except User.DoesNotExist:
            pass

        return render(request, "forgot_password.html", {"success": True})

    return render(request, "forgot_password.html")

def reset_password_view(request, token):
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        return render(request, 'reset_password.html', {'error': 'Invalid or expired link.'})

    if not token_obj.is_valid():
        return render(request, 'reset_password.html', {'error': 'This link has expired. Request a new one.'})

    if request.method == 'POST':
        p1 = request.POST.get('password1', '')
        p2 = request.POST.get('password2', '')
        if p1 != p2:
            return render(request, 'reset_password.html', {'error': 'Passwords do not match.', 'token': token})
        if len(p1) < 8:
            return render(request, 'reset_password.html', {'error': 'Password too short.', 'token': token})

        token_obj.user.set_password(p1)
        token_obj.user.save()
        token_obj.used = True
        token_obj.save()
        return redirect('login')

    return render(request, 'reset_password.html', {'token': token})


@login_required
def dashboard_view(request):
    all_chunks = vector_store.get_all_chunks()
    sources = {m.get('source') for m in all_chunks.get('metadatas', []) if m}
    chunk_count = len(all_chunks.get('ids', []))
    query_count = LLMCallLog.objects.filter(user=request.user).count()

    context = {
        "chunk_count": chunk_count,
        "query_count": query_count,
        'doc_count': len(sources),
    }
    return render(request, "dashboard.html", context)

@login_required
def ragchat_view(request):
    sessions = ChatSession.objects.filter(user=request.user)[:20]
    return render(request, "ragchat.html", {"sessions": sessions})

@login_required
def profile_view(request):
    if request.method == "POST":
        action = request.POST.get("action", "update_info")

        if action == "update_info":
            u = request.user
            u.first_name = request.POST.get("first_name", u.first_name)
            u.last_name = request.POST.get("last_name", u.last_name)
            u.email = request.POST.get("email", u.email)
            u.save()

            profile, _ = UserProfile.objects.get_or_create(user=u)
            profile.bio = request.POST.get("bio", profile.bio)
            profile.save()

        elif action == "change_password":
            old_pw = request.POST.get("old_password")
            new_pw1 = request.POST.get("new_password1")
            new_pw2 = request.POST.get("new_password2")

            if not request.user.check_password(old_pw):
                return render(request, "profile.html", {"pw_error": "Old password is incorrect."})
            if new_pw1 != new_pw2:
                return render(request, "profile.html", {"pw_error": "New passwords do not match."})
            request.user.set_password(new_pw1)
            request.user.save()
            login(request, request.user)        ## re-auth after password change

        return redirect("profile")
    
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    context = {
        "profile": profile,
        "doc_count": 0,
        "query_count": LLMCallLog.objects.filter(user=request.user).count(),
        "days_active": (timezone.now().date() - request.user.date_joined.date()).days,
    }
    return render(request, "profile.html", context)

@login_required
def upload_view(request):
    return render(request, "upload_document.html")


@login_required
def vector_store_view(request):
    all_chunks = vector_store.get_all_chunks()
    docs_map   = {}

    for cid, content, meta in zip(
        all_chunks.get('ids', []),
        all_chunks.get('documents', []),
        all_chunks.get('metadatas', []),
    ):
        source = meta.get('source', 'unknown') if meta else 'unknown'
        if source not in docs_map:
            docs_map[source] = {
                'id': source, 'name': source.split('/')[-1],
                'source': source, 'ext': source.rsplit('.', 1)[-1].lower(),
                'chunk_count': 0, 'size': '—', 'status': 'indexed', 'date': '—',
            }
        docs_map[source]['chunk_count'] += 1

    chunks = [
        {'id': cid, 'content': doc or '', 'source': (meta or {}).get('source', '—'),
         'tokens': len((doc or '').split())}
        for cid, doc, meta in zip(
            all_chunks.get('ids', []),
            all_chunks.get('documents', []),
            all_chunks.get('metadatas', []),
        )
    ]

    return render(request, 'vector_store.html', {
        'documents':   list(docs_map.values()),
        'chunks':      chunks,
        'doc_count':   len(docs_map),
        'chunk_count': len(chunks),
    })


@login_required
def llm_stats_view(request):
    time_range = request.GET.get('range', '24h')
    delta_map  = {'1h': 1, '24h': 24, '7d': 168, '30d': 720}
    hours      = delta_map.get(time_range, 24)
    since      = timezone.now() - timedelta(hours=hours)

    logs = LLMCallLog.objects.filter(user=request.user, created_at__gte=since)

    agg = logs.aggregate(
        total_calls   = Count('id'),
        avg_latency   = Avg('latency_sec'),
        avg_tps       = Avg('tokens_per_sec'),
        total_tokens  = Sum('total_tokens'),
    )

    calls_json = list(logs.values(
        'id', 'model', 'prompt', 'response',
        'prompt_tokens', 'compl_tokens', 'total_tokens',
        'latency_sec', 'tokens_per_sec', 'status', 'created_at',
    )[:200])

    # Make serializable
    for c in calls_json:
        c['id']         = str(c['id'])
        c['ts']         = c.pop('created_at').strftime('%H:%M:%S')
        c['latency']    = c.pop('latency_sec')
        c['tps']        = c.pop('tokens_per_sec')
        c['promptTok']  = c.pop('prompt_tokens')
        c['complTok']   = c.pop('compl_tokens')

    return render(request, 'llm_stats.html', {
        'total_calls':    agg['total_calls'] or 0,
        'avg_latency':    round(agg['avg_latency'] or 0, 2),
        'avg_tps':        round(agg['avg_tps'] or 0, 1),
        'total_tokens':   round((agg['total_tokens'] or 0) / 1000, 1),
        'est_cost':       round((agg['total_tokens'] or 0) * 0.0000045, 4),
        'llm_calls_json': json.dumps(calls_json),
    })

@login_required
def new_chat_view(request):
    """POST → create new session, return session id"""
    if request.method == 'POST':
        session = ChatSession.objects.create(user=request.user, title='New Chat')
        return JsonResponse({'session_id': str(session.id), 'title': session.title})
    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
def chat_history_view(request):
    """GET all sessions with their messages"""
    sessions = ChatSession.objects.filter(user=request.user).prefetch_related('messages')
    data = [
        {
            'session_id': str(s.id),
            'title':      s.title,
            'updated_at': s.updated_at.isoformat(),
            'messages': [
                {
                    'role':       m.role,
                    'content':    m.content,
                    'sources':    m.sources,
                    'created_at': m.created_at.isoformat(),
                }
                for m in s.messages.all()
            ],
        }
        for s in sessions
    ]
    return JsonResponse({'sessions': data})


@login_required
def clear_chat_queue_view(request):
    """DELETE a specific session"""
    if request.method == 'DELETE':
        data       = json.loads(request.body or '{}')
        session_id = data.get('session_id')
        deleted, _ = ChatSession.objects.filter(id=session_id, user=request.user).delete()
        if deleted:
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'error': 'Session not found'}, status=404)
    return JsonResponse({'error': 'DELETE required'}, status=405)

class UploadDocumentView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=drf_status.HTTP_400_BAD_REQUEST)
        try:
            ingestion_service.ingest_file(file)
            return Response({'status': 'ok', 'filename': file.name})
        except Exception as e:
            return Response({'error': str(e)}, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class CheckChunkView(APIView):
    def get(self, request):
        chunks = vector_store.get_all_chunks()
        return Response({'count': len(chunks.get('ids', [])), 'chunks': chunks})


class SimilaritySearchView(APIView):
    def post(self, request):
        query = request.data.get('query', '')
        k     = int(request.data.get('k', 5))
        results = vector_store.similarity_search(query, k=k)
        return Response({'results': [{'content': d.page_content, 'metadata': d.metadata} for d in results]})

    
class QueryAPIView(APIView):
    def post(self, request):
        question   = request.data.get('question', '').strip()
        session_id = request.data.get('session_id')

        if not question:
            return Response({'error': 'question required'}, status=drf_status.HTTP_400_BAD_REQUEST)

        # Get or create session
        session = None
        if session_id:
            session = ChatSession.objects.filter(id=session_id, user=request.user).first()
        if not session:
            session = ChatSession.objects.create(user=request.user, title=question[:60])

        # Save user message
        ChatMessage.objects.create(session=session, role='user', content=question)

        # Run agent
        agent  = AgenticService()
        result = agent.ask(question, user=request.user, session=session)

        answer  = result.get('answer', '')
        sources = result.get('sources', [])

        # Update session title if it's the first message
        if session.messages.count() <= 2:
            session.title = question[:60]
            session.save()

        # Save assistant message
        ChatMessage.objects.create(
            session=session, role='assistant',
            content=answer, sources=sources,
        )

        return Response({
            'answer':     answer,
            'sources':    sources,
            'session_id': str(session.id),
        })


@login_required
@require_http_methods(['DELETE'])
def delete_document_view(request, doc_id):
    try:
        all_chunks     = vector_store.get_all_chunks()
        ids_to_delete  = [
            cid for cid, meta in zip(
                all_chunks.get('ids', []),
                all_chunks.get('metadatas', [])
            )
            if str((meta or {}).get('source', '')).endswith(str(doc_id))
        ]
        if ids_to_delete:
            vector_store.db.delete(ids=ids_to_delete)
        return JsonResponse({'status': 'ok', 'deleted': len(ids_to_delete)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
@login_required
@require_http_methods(['DELETE'])
def delete_chunk_view(request, chunk_id):
    try:
        vector_store.db.delete(ids=[chunk_id])
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(['POST'])
def edit_chunk_view(request):
    try:
        data      = json.loads(request.body)
        chunk_id  = data.get('id')
        content   = data.get('content')
        vector_store.db.update_documents(ids=[chunk_id], documents=[content])
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(['POST'])
def purge_vector_store_view(request):
    try:
        all_chunks = vector_store.get_all_chunks()
        ids        = all_chunks.get('ids', [])
        if ids:
            vector_store.db.delete(ids=ids)
        return JsonResponse({'status': 'ok', 'deleted': len(ids)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    