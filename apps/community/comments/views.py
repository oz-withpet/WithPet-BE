# apps/community/comments/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.community.common.comments_preview import preview_comments
from apps.community.comments.serializers import CommentsBlockOut
from .services import create as create_comment, update as update_comment, delete as delete_comment


class PostCommentsView(APIView):
    """
    GET  /posts/{post_id}/comments  → 댓글 목록
    POST /posts/{post_id}/comments  → 댓글 생성
    """

    def get(self, request, post_id: int, *args, **kwargs):
        limit = int(request.query_params.get("limit", 20) or 20)
        after_raw = request.query_params.get("after")
        after_id = int(after_raw) if (after_raw and after_raw.isdigit()) else None

        data = preview_comments(post_id=post_id, limit=limit, after_id=after_id)
        ser = CommentsBlockOut(data)
        return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request, post_id: int, *args, **kwargs):
        # 로그인 체크는 services.create 내부에서 _require_login으로 이미 함
        return create_comment(request, post_id)


class CommentModifyView(APIView):
    """
    PUT    /comments/{comment_id}  → 수정
    DELETE /comments/{comment_id}  → 삭제
    """
    permission_classes = (IsAuthenticated,)

    def put(self, request, comment_id: int, *args, **kwargs):
        return update_comment(request, comment_id)

    def delete(self, request, comment_id: int, *args, **kwargs):
        return delete_comment(request, comment_id)
