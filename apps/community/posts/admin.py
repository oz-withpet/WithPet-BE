from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import SuspiciousFileOperation
from django.utils import timezone

from .models import Post, PostCategory, PostImage

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0
    fields = ("image", "order", "created_at")
    readonly_fields = ("created_at",)

@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("id",)


@admin.action(description="선택한 게시글 소프트 삭제")
def soft_delete_posts(modeladmin, request, queryset):
    now = timezone.now()
    updated = queryset.update(is_deleted=True, deleted_at=now)
    modeladmin.message_user(request, f"{updated}건 소프트 삭제 완료")

@admin.action(description="선택한 게시글 복구")
def restore_posts(modeladmin, request, queryset):
    updated = queryset.update(is_deleted=False, deleted_at=None)
    modeladmin.message_user(request, f"{updated}건 복구 완료")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "category", "author",
        "view_count", "like_count", "comment_count",
        "is_deleted", "created_at", "updated_at", "image_thumb",
    )
    list_filter = ("category", "is_deleted", "created_at")
    search_fields: tuple[str, ...] = ()

    raw_id_fields = ("author",)
    autocomplete_fields = ("category",)

    readonly_fields = ("view_count", "like_count", "comment_count", "created_at", "updated_at")
    ordering = ("-created_at", "-id")
    date_hierarchy = "created_at"
    list_select_related = ("category", "author")

    actions = (soft_delete_posts, restore_posts)
    inlines = [PostImageInline]

    def get_search_fields(self, request):
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
