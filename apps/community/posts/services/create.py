# apps/community/posts/services/create.py
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.community.posts.models import Post, PostCategory, PostImage
from apps.community.posts.serializers import PostCreateIn
from apps.community.common.id_codec import id_to_public

MAX_IMAGES = 5

def _validate_images_count(existing_legacy: int, new_files_count: int):
    total = existing_legacy + new_files_count
    if total > MAX_IMAGES:
        raise ValidationError({"images": f"이미지는 최대 {MAX_IMAGES}장까지 업로드할 수 있습니다."})

def create_post(request):
    ser = PostCreateIn(data=request.data, context={"request": request})
    ser.is_valid(raise_exception=True)
    data = ser.validated_data

    try:
        category = PostCategory.objects.get(name=data["category"])
    except PostCategory.DoesNotExist:
        raise ValidationError({"category": "등록되지 않은 카테고리입니다. 관리자에게 문의하세요."})

    legacy_single = data.get("image")
    files = request.FILES.getlist("images")

    existing_legacy = 1 if legacy_single else 0
    _validate_images_count(existing_legacy, len(files))

    with transaction.atomic():
        post = Post.objects.create(
            author_id=request.user.id,
            category=category,
            title=data["title"],
            content=data["content"],
            image=legacy_single if legacy_single else None,
        )

        if files:
            objs = [
                PostImage(post=post, image=f, order=idx)
                for idx, f in enumerate(files)
            ]
            PostImage.objects.bulk_create(objs, batch_size=50)

    pub_id = id_to_public(post.id)
    headers = {"Location": f"/posts/{pub_id}"}
    return Response({"post_id": pub_id}, status=status.HTTP_201_CREATED, headers=headers)
