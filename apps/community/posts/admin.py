from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import SuspiciousFileOperation

from .models import Post, PostCategory


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("id",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "category", "author",
        "view_count", "like_count", "comment_count",
        "is_deleted", "created_at", "updated_at", "image_thumb",
    )
    list_filter = ("category", "is_deleted", "created_at")
    search_fields: tuple[str, ...] = ()  # 실제 필드는 get_search_fields에서 동적 구성

    # ✅ users.Admin 의존 제거: author는 raw_id_fields로, category만 autocomplete 유지
    raw_id_fields = ("author",)
    autocomplete_fields = ("category",)

    readonly_fields = ("view_count", "like_count", "comment_count", "created_at", "updated_at")
    ordering = ("-created_at", "-id")
    date_hierarchy = "created_at"
    list_select_related = ("category", "author")

    def get_search_fields(self, request):
        """
        사용자 모델에 존재하는 필드만 안전하게 추가.
        우선순위: username/email/nickname/name → 항상 author__id 보조.
        """
        base = ["title", "content"]
        user_model = get_user_model()
        user_field_names = {
            f.name for f in user_model._meta.get_fields() if isinstance(f, models.Field)
        }
        for cand in ("username", "email", "nickname", "name"):
            if cand in user_field_names:
                base.append(f"author__{cand}")
        base.append("author__id")
        return tuple(base)

    def image_thumb(self, obj):
        image = getattr(obj, "image", None)
        if not image or not getattr(image, "name", ""):
            return "-"
        try:
            url = image.url
        except (ValueError, SuspiciousFileOperation):
            return "-"
        return format_html(
            '<img src="{}" width="70" style="object-fit:cover;border-radius:6px;" />',
            url,
        )
    image_thumb.short_description = "이미지"
