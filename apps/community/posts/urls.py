from django.urls import path
from .views import PostsListView

urlpatterns = [
    # GET /posts
    path("posts", PostsListView.as_view(), name="posts-list"),
]