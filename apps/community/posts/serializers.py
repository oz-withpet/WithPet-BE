from rest_framework import serializers
from apps.community.comments.serializers import CommentsBlockOut
from apps.community.common import Base64IDField, CATEGORY_KOR_ALLOWED, id_to_public
from .models import Post

class PostCreateIn(serializers.Serializer):
    title = serializers.CharField(min_length=1, max_length=100)
    content = serializers.CharField(min_length=1, max_length=20000)
    category = serializers.ChoiceField(
        choices=CATEGORY_KOR_ALLOWED,
        error_messages={
            "invalid_choice": "카테고리는 자유게시판/정보공유/질문게시판만 허용됩니다.",
        },
    )
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
    # 스펙: multipart 교체 이미지(옵션)
    image = serializers.ImageField(required=False, allow_null=True, write_only=True)

    @staticmethod
    def validate_category(value):
        if value is None:
            return value
        if value not in CATEGORY_KOR_ALLOWED:
            raise serializers.ValidationError(
                "카테고리는 자유게시판/정보공유/질문게시판만 허용됩니다."
            )
        return value


# ===== 출력 =====
class PostListItemMainOut(serializers.ModelSerializer):
    id = Base64IDField(source="pk", read_only=True)
    image_url = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ("id", "title", "image_url", "author")

    @staticmethod
    def get_image_url(obj):
        f = getattr(obj, "image", None)
        return f.url if f else None

    @staticmethod
    def get_author(obj):
        # Author.user_id도 base64로 노출
        uid = id_to_public(obj.author_id) if obj.author_id is not None else None
        return {"user_id": uid, "nickname": ""}


class PostListItemCommunityOut(serializers.ModelSerializer):
    id = Base64IDField(source="pk", read_only=True)
    content_snippet = serializers.SerializerMethodField()
    category = serializers.CharField(source="category.name", allow_null=True)
    image_url = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    is_liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content_snippet",
            "category",
            "image_url",
            "author",
            "created_at",
            "updated_at",
            "view_count",
            "like_count",
            "comment_count",
            "is_liked_by_me",
        )

    @staticmethod
    def get_content_snippet(obj):
        return (obj.content or "")[:200]

    @staticmethod
    def get_image_url(obj):
        f = getattr(obj, "image", None)
        return f.url if f else None

    @staticmethod
    def get_author(obj):
        uid = id_to_public(obj.author_id) if obj.author_id is not None else None
        return {"user_id": uid, "nickname": ""}

    @staticmethod
    def get_is_liked_by_me(obj):
        return bool(getattr(obj, "_is_liked_by_me", False))


class PostDetailOut(PostListItemCommunityOut):
    content = serializers.CharField()

    class Meta(PostListItemCommunityOut.Meta):
        fields = PostListItemCommunityOut.Meta.fields + ("content",)


class PostDetailResponseOut(serializers.Serializer):
    post = PostDetailOut()
    comments = CommentsBlockOut(required=False)
