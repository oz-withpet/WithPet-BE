# apps/community/comments/urls.py (예시)
from django.urls import path
from .views import PostCommentsView, CommentModifyView

urlpatterns = [
    path("posts/<int:post_id>/comments", PostCommentsView.as_view(), name="post-comments"),
    path("comments/<int:comment_id>", CommentModifyView.as_view(), name="comment-modify"),
]
