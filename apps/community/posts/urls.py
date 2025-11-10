# apps/community/posts/urls.py
from django.urls import path
from .views import PostsView

urlpatterns = [
    # GET  /posts  -> 목록 (view=community | main)
    # POST /posts  -> 생성 (JSON & multipart, 이미지 옵션)
    path("posts", PostsView.as_view(), name="posts"),
]
