# apps/community/posts/serializers.py
from __future__ import annotations

from typing import Optional, List

from rest_framework import serializers
from apps.community.comments.serializers import CommentsBlockOut
from apps.community.common import Base64IDField, CATEGORY_KOR_ALLOWED, id_to_public
from .models import Post


# ---------- 입력 ----------

class PostCreateIn(serializers.Serializer):
    title = serializers.CharField(min_length=1, max_length=100)
    content = serializers.CharField(min_length=1, max_length=20000)
    category = serializers.ChoiceField(
        choices=CATEGORY_KOR_ALLOWED,
        error_messages={
            "invalid_choice": "카테고리는 자유게시판/정보공유/질문게시판만 허용됩니다.",
        },
    )
    # ⚠️ 업로드 파일은 서비스에서 request.FILES.getlist("images")로 처리
    # 하위호환용 단일 이미지(있으면 사용)
    image = serializers.ImageField(required=False, allow_null=True, write_only=True)

    @staticmethod
    def validate_category(value: str) -> str:
        if value not in CATEGORY_KOR_ALLOWED:
            raise serializers.ValidationError(
                "카테고리는 자유게시판/정보공유/질문게시판만 허용됩니다."
            )
        return value


class PostUpdateIn(serializers.Serializer):
    title = serializers.CharField(min_length=1, max_length=100, required=False, allow_null=True)
    content = serializers.CharField(min_length=1, max_length=20000, required=False, allow_null=True)
    category = serializers.ChoiceField(choices=CATEGORY_KOR_ALLOWED, required=False, allow_null=True)
    image_delete = serializers.BooleanField(required=False, allow_null=True)
    # ⚠️ multipart로 넘어온 추가 이미지들은 서비스에서 request.FILES.getlist("images")로 처리
    image = serializers.ImageField(required=False, allow_null=True, write_only=True)  # 하위호환
    # 선택: 개별 삭제용 이미지 id 리스트(서비스에서 사용)
    image_ids_delete = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
        write_only=True,
    )

    @staticmethod
    def validate_category(value):
        if value is None:
            return value
        if value not in CATEGORY_KOR_ALLOWED:
            raise serializers.ValidationError(
                "카테고리는 자유게시판/정보공유/질문게시판만 허용됩니다."
            )
        return value


# ---------- 공통(출력용) 유틸 ----------

class _ImageURLMixin:
    """첫 장(썸네일)과 전체 이미지 URL 배열을 만들어주는 믹스인."""

    def _abs(self, url: Optional[str]) -> Optional[str]:
        if not url:
            return None
        req = self.context.get("request") if hasattr(self, "context") else None
        try:
            return req.build_absolute_uri(url) if req else url
        except Exception:
            return url

    def _first_image_url(self, obj: Post) -> Optional[str]:
        # 새 구조: post.images.first()
        rel = getattr(obj, "images", None)
        if rel and hasattr(rel, "first"):
            first = rel.first()
            if first and getattr(first, "image", None) and getattr(first.image, "url", None):
                return self._abs(first.image.url)

        # 하위호환: Post.image 단일 필드
        legacy = getattr(obj, "image", None)
        if legacy and getattr(legacy, "url", None):
            return self._abs(legacy.url)
        return None

    def _all_image_urls(self, obj: Post) -> List[str]:
        urls: List[str] = []
        rel = getattr(obj, "images", None)
        if rel and hasattr(rel, "all"):
            for pi in rel.all():
                url = getattr(getattr(pi, "image", None), "url", None)
                if url:
                    absu = self._abs(url)
                    if absu:
                        urls.append(absu)
        else:
            # 하위호환: 단일 이미지만 있는 경우
            legacy = getattr(obj, "image", None)
            if legacy and getattr(legacy, "url", None):
                absu = self._abs(legacy.url)
                if absu:
                    urls.append(absu)
        return urls


# ---------- 출력: 항상 "풍부한 버전" ----------

class PostListItemFullOut(serializers.ModelSerializer, _ImageURLMixin):
    """
    목록에서도 상세와 거의 동일한 풍부한 정보 제공:
    - 기본 필드 + content + 이미지 배열 + 좋아요 여부
    """
    id = Base64IDField(source="pk", read_only=True)
    category = serializers.CharField(source="category.name", allow_null=True)
    author = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()     # 대표(첫 장)
    images = serializers.SerializerMethodField()        # 전체 이미지 배열
    is_liked_by_me = serializers.SerializerMethodField()
    content = serializers.CharField()

    class Meta:
        model = Post
        fields = (
            "id", "title", "content", "category",
            "image_url", "images", "author",
            "created_at", "updated_at",
            "view_count", "like_count", "comment_count",
            "is_liked_by_me",
        )

    def get_author(self, obj: Post):
        uid = id_to_public(obj.author_id) if obj.author_id is not None else None
        return {"user_id": uid, "nickname": ""}

    def get_image_url(self, obj: Post) -> Optional[str]:
        return self._first_image_url(obj)

    def get_images(self, obj: Post) -> List[str]:
        return self._all_image_urls(obj)

    @staticmethod
    def get_is_liked_by_me(obj: Post) -> bool:
        if hasattr(obj, "is_liked_by_me"):
            return bool(getattr(obj, "is_liked_by_me"))
        return bool(getattr(obj, "_is_liked_by_me", False))


# 과거 이름을 그대로 유지하되, 이제는 "풀 버전"을 상속만 함.
class PostListItemMainOut(PostListItemFullOut):
    pass


class PostListItemCommunityOut(PostListItemFullOut):
    pass


class PostDetailOut(PostListItemCommunityOut):
    """
    상세도 목록과 동일한 풍부한 필드를 유지.
    (별도 필드 추가가 없으므로 그대로 상속)
    """
    pass


class PostDetailResponseOut(serializers.Serializer):
    post = PostDetailOut()
    comments = CommentsBlockOut(required=False)
