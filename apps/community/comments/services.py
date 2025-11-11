from __future__ import annotations
import binascii
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.community.common import id_from_public, id_to_public
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


def create(request, post_id: str):
    """
    POST /posts/{post_id}/comments
    응답: 201 {"comment_id": "<base64>"}
    """
    # 401
    r = _require_login(request)
    if r:
        return r

    # body 검증
    ser = CommentCreateIn(data=request.data)
    ser.is_valid(raise_exception=True)

    # post_id(base64) → int
    try:
        internal_pid = id_from_public(post_id)
    except (ValueError, binascii.Error):
        raise ValidationError({"post_id": "유효하지 않은 base64 ID입니다."})

    # ✅ QuerySet 대신 "모델 클래스"를 첫 인자로 전달 → 타입 경고 제거
    get_object_or_404(Post, id=internal_pid, is_deleted=False)

    with transaction.atomic():
        c = Comment.objects.create(
            post_id=internal_pid,       # post 객체를 다시 안 가져와도 됨
            author=request.user,
            content=ser.validated_data["content"],
        )

    return Response({"comment_id": id_to_public(c.id)}, status=status.HTTP_201_CREATED)


def update(request, comment_id: str):
    """
    PUT /comments/{comment_id}
    응답: 200 {"comment_id": "<base64>", "updated_at": "<ISO8601>"}
    """
    # 401
    r = _require_login(request)
    if r:
        return r

    ser = CommentUpdateIn(data=request.data)
    ser.is_valid(raise_exception=True)

    try:
        cid = id_from_public(comment_id)
    except (ValueError, binascii.Error):
        raise ValidationError({"comment_id": "유효하지 않은 base64 ID입니다."})

    # ✅ 모델 클래스 사용 → 타입 경고 제거
    comment = get_object_or_404(Comment, id=cid, is_deleted=False)

    # 소유자 검사(관리자 허용)
    user = request.user
    if comment.author_id != user.id and not user.is_staff:
        raise PermissionDenied(detail={"code": "FORBIDDEN", "message": "권한이 없습니다."})

    comment.content = ser.validated_data["content"]
    comment.save(update_fields=["content", "updated_at"])  # auto_now 갱신

    return Response(
        {"comment_id": id_to_public(comment.id), "updated_at": comment.updated_at},
        status=status.HTTP_200_OK,
    )


def delete(request, comment_id: str):
    """
    DELETE /comments/{comment_id}
    응답: 204 No Content
    """
    # 401
    r = _require_login(request)
    if r:
        return r

    try:
        cid = id_from_public(comment_id)
    except (ValueError, binascii.Error):
        raise ValidationError({"comment_id": "유효하지 않은 base64 ID입니다."})

    # ✅ 모델 클래스 사용 → 타입 경고 제거
    comment = get_object_or_404(Comment, id=cid)

    # 소유자 검사(관리자 허용)
    user = request.user
    if comment.author_id != user.id and not user.is_staff:
        raise PermissionDenied(detail={"code": "FORBIDDEN", "message": "권한이 없습니다."})

    # 정책: 소프트 삭제가 있으면 사용, 없으면 하드 삭제
    if hasattr(comment, "is_deleted"):
        if not comment.is_deleted:
            comment.is_deleted = True
            comment.save(update_fields=["is_deleted", "updated_at"])
    else:
        comment.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
