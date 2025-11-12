from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.community.posts.models import Post, PostCategory
from apps.community.posts.serializers import PostCreateIn
from apps.community.common.id_codec import id_to_public

def create_post(request):
    # DRF 파서(JSON/multipart)로 파싱된 데이터 사용
    ser = PostCreateIn(data=request.data, context={"request": request})
    ser.is_valid(raise_exception=True)
    data = ser.validated_data

    # 카테고리 매핑 (시드 전제)
    try:
        category = PostCategory.objects.get(name=data["category"])
    except PostCategory.DoesNotExist:
        raise ValidationError({"category": "등록되지 않은 카테고리입니다. 관리자에게 문의하세요."})

    image = data.get("image")

    with transaction.atomic():
        post = Post.objects.create(
            author_id=request.user.id,     # 인증 필요
            category=category,
            title=data["title"],
            content=data["content"],
            image=image if image else None,
        )

    pub_id = id_to_public(post.id)        # 외부 노출용 base64
    headers = {"Location": f"/posts/{pub_id}"}
    return Response({"post_id": pub_id}, status=status.HTTP_201_CREATED, headers=headers)
