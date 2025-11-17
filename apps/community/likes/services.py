from __future__ import annotations
import binascii
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status as http_status            # ✅ 별칭 사용
from rest_framework.exceptions import ValidationError

from apps.community.common import id_from_path_param
from apps.community.posts.models import Post
from .models import Like


def _require_login(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return Response(
            {"code": "UNAUTHORIZED", "message": "로그인이 필요합니다."},
            status=http_status.HTTP_401_UNAUTHORIZED,          # ✅ http_status
        )
    return None


def _decode_post_id_or_400(post_b64: str) -> int:
    try:
        return id_from_path_param(post_b64)
    except (ValueError, binascii.Error):
        raise ValidationError({"post_id": "유효하지 않은 base64 ID입니다."})


def status(request, post_id: str) -> Response:
    pid = _decode_post_id_or_400(post_id)
    post = get_object_or_404(Post, id=pid, is_deleted=False)

    is_liked = False
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        ct = ContentType.objects.get_for_model(Post)
        is_liked = Like.objects.filter(
            user_id=user.id, content_type=ct, object_id=pid
        ).exists()

    return Response(
        {"is_liked": is_liked, "like_count": post.like_count},
        status=http_status.HTTP_200_OK,
    )


def on(request, post_id: str) -> Response:
    r = _require_login(request)
    if r:
        return r

    pid = _decode_post_id_or_400(post_id)
    get_object_or_404(Post, id=pid, is_deleted=False)

    user_id = request.user.id
    ct = ContentType.objects.get_for_model(Post)

    with transaction.atomic():
        _, created = Like.objects.get_or_create(
            user_id=user_id, content_type=ct, object_id=pid
        )
        if created:
            Post.objects.filter(id=pid).update(like_count=F("like_count") + 1)

        current = Post.objects.only("like_count").get(id=pid).like_count

    return Response({"is_liked": True, "like_count": current}, status=http_status.HTTP_200_OK)


def off(request, post_id: str) -> Response:
    r = _require_login(request)
    if r:
        return r

    pid = _decode_post_id_or_400(post_id)
    get_object_or_404(Post, id=pid, is_deleted=False)

    user_id = request.user.id
    ct = ContentType.objects.get_for_model(Post)

    with transaction.atomic():
        deleted, _ = Like.objects.filter(
            user_id=user_id, content_type=ct, object_id=pid
        ).delete()
        if deleted:
            Post.objects.filter(id=pid).update(like_count=F("like_count") - 1)

        current = Post.objects.only("like_count").get(id=pid).like_count

    return Response({"is_liked": False, "like_count": current}, status=http_status.HTTP_200_OK)
