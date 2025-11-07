from rest_framework import serializers
from apps.community.common import Base64IDField, id_to_public
from .models import Comment


# ===== 입력 =====
class CommentCreateIn(serializers.Serializer):
    content = serializers.CharField(min_length=1, max_length=5000)


class CommentUpdateIn(serializers.Serializer):
    content = serializers.CharField(min_length=1, max_length=5000)


# ===== 출력 =====
class CommentOut(serializers.ModelSerializer):
    id = Base64IDField(source="pk", read_only=True)
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "author", "content", "created_at", "updated_at", "is_deleted")

    @staticmethod
    def get_author(obj):
        uid = id_to_public(obj.author_id) if obj.author_id is not None else None
        return {"user_id": uid, "nickname": ""}


# 댓글 프리뷰/페이지네이션 컨테이너 (스펙: CommentsBlock)
class CommentsBlockOut(serializers.Serializer):
    items = CommentOut(many=True)
    total_count = serializers.IntegerField()
    has_next = serializers.BooleanField()
    next_after = serializers.CharField(allow_null=True)
