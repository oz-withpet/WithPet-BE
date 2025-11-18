from django.urls import path
from .views import PostCommentCreateView, CommentModifyView

app_name = "comments"

urlpatterns = [
    path("posts/<int:post_id>/comments", PostCommentCreateView.as_view(), name="comment-create"),
    path("comments/<int:comment_id>", CommentModifyView.as_view(), name="comment-modify"),
]
