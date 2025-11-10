from django.urls import path
from .views import PostsView

urlpatterns = [
    # GET /posts
    path("posts", PostsView.as_view(), name="posts"),
]