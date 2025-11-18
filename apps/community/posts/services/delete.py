from __future__ import annotations

from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.community.posts.models import Post


def _alive_queryset():
    try:
        return Post.objects.alive()
    except AttributeError:
        return Post.objects.filter(is_deleted=False)


def delete_post(request, post_id: int) -> Response:
    pk = int(post_id)

    try:
        post = _alive_queryset().only("id", "author_id", "is_deleted").get(pk=pk)
    except Post.DoesNotExist:
        raise NotFound("게시글을 찾을 수 없습니다.")

    user = request.user
    if not user.is_authenticated:
        raise PermissionDenied("로그인이 필요합니다.")
    if post.author_id != user.id:
        raise PermissionDenied("본인 글만 삭제할 수 있습니다.")

    post.is_deleted = True
    post.deleted_at = timezone.now()
    post.save(update_fields=["is_deleted", "deleted_at"])

    return Response(status=status.HTTP_204_NO_CONTENT)
