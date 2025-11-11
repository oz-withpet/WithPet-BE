from django.contrib import admin
from .models import Comment
from apps.community.common import id_to_public

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id_b64", "post_id_b64", "author_id", "short_content", "is_deleted", "created_at")
    list_filter = ("is_deleted", "created_at")
    search_fields = ("content",)
    raw_id_fields = ("post", "author")  # ✅ User Admin 없어도 동작
    readonly_fields = ("created_at", "updated_at")

    def id_b64(self, obj):
        return id_to_public(obj.id)
    id_b64.short_description = "ID(b64)"

    def post_id_b64(self, obj):
        return id_to_public(obj.post_id)
    post_id_b64.short_description = "Post(b64)"

    def short_content(self, obj):
        txt = obj.content or ""
        return (txt[:30] + "…") if len(txt) > 31 else txt
    short_content.short_description = "내용(요약)"

