
from django.urls import path
from .views import PostsView, PostDetailView



urlpatterns = [
    path("posts", PostsView.as_view(), name="posts"),
    path("posts/<str:post_id>", PostDetailView.as_view(), name="post-detail"),
]
