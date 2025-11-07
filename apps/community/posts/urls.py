from django.urls import path
from .views import PostsListView

urlpatterns = [
    path("posts", PostsListView.as_view(), name="posts-list"),
]