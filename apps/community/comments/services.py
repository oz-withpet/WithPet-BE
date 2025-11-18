# apps/community/comments/services.py
from __future__ import annotations

from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.community.posts.models import Post
from .models import Comment
from .serializers import CommentCreateIn, CommentUpdateIn


def _require_login(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return Response(
            {"code": "UNAUTHORIZED", "message": "로그인이 필요합니다."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    return None


def create(request, post_id: int):
    """
    댓글 생성: post_id는 URL에서 <int:post_id>로 들어오는 정수 PK
    """
    r = _require_login(request)
    if r:
        return r

    # body 검증
    ser = CommentCreateIn(data=request.data)
    ser.is_valid(raise_exception=True)

    # post_id는 이미 int이므로 바로 사용
    internal_pid = int(post_id)

    # 삭제되지 않은 게시글인지 확인
    get_object_or_404(Post, id=internal_pid, is_deleted=False)

    with transaction.atomic():
        c = Comment.objects.create(
            post_id=internal_pid,
            author=request.user,
            content=ser.validated_data["content"],
        )

    return Response({"comment_id": int(c.id)}, status=status.HTTP_201_CREATED)


def update(request, comment_id: int):
    """
    댓글 수정: comment_id도 <int:comment_id>로 들어오는 정수 PK
    """
    r = _require_login(request)
    if r:
        return r

    ser = CommentUpdateIn(data=request.data)
    ser.is_valid(raise_exception=True)

    # 방어적으로 캐스팅 (내부에서 str로 호출될 가능성 대비)
    try:
        cid = int(comment_id)
    except (ValueError, TypeError):
        raise ValidationError({"comment_id": "유효하지 않은 정수 ID입니다."})

    comment = get_object_or_404(Comment, id=cid, is_deleted=False)

    user = request.user
    if comment.author_id != user.id and not user.is_staff:
        raise PermissionDenied(detail={"code": "FORBIDDEN", "message": "권한이 없습니다."})

    comment.content = ser.validated_data["content"]
    comment.save(update_fields=["content", "updated_at"])  # auto_now 갱신

    return Response(
        {
            "comment_id": int(comment.id),
            "updated_at": comment.updated_at,  # DRF가 DateTimeField 알아서 직렬화
        },
        status=status.HTTP_200_OK,
    )


def delete(request, comment_id: int):
    """
    댓글 삭제: comment_id 정수 PK
    """
    r = _require_login(request)
    if r:
        return r

    try:
        cid = int(comment_id)
    except (ValueError, TypeError):
        raise ValidationError({"comment_id": "유효하지 않은 정수 ID입니다."})

    comment = get_object_or_404(Comment, id=cid)
    user = request.user
    if comment.author_id != user.id and not user.is_staff:
        raise PermissionDenied(detail={"code": "FORBIDDEN", "message": "권한이 없습니다."})

    if hasattr(comment, "is_deleted"):
        if not comment.is_deleted:
            comment.is_deleted = True
            comment.save(update_fields=["is_deleted", "updated_at"])
    else:
        comment.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
