# apps/community/comments/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .services import create as create_comment, update as update_comment, delete as delete_comment

class PostCommentCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, post_id: str, *args, **kwargs):
        return create_comment(request, post_id)

class CommentModifyView(APIView):
    permission_classes = (IsAuthenticated,)
    def put(self, request, comment_id: str, *args, **kwargs):
        return update_comment(request, comment_id)

    def delete(self, request, comment_id: str, *args, **kwargs):
        return delete_comment(request, comment_id)
