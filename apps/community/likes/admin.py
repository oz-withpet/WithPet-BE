# apps/community/likes/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from .models import Like
from apps.community.common import id_to_public


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "target_str", "created_at")
    list_filter = ("content_type", "created_at")
    # 숫자 필드는 정확 일치 룩업으로 지정
    search_fields = ("user__id__exact", "object_id__exact")
    raw_id_fields = ("user",)  # User Admin 의존 없음
    date_hierarchy = "created_at"
    ordering = ("-created_at", "-id")
    list_select_related = ("user", "content_type")
    readonly_fields = ("created_at",)
    fields = ("user", "content_type", "object_id", "created_at")

    def get_search_fields(self, request):
        """
        기본(정확 일치) + 사용자 텍스트 필드가 있을 경우 contains 검색 추가
        """
        fields = list(self.search_fields)  # ("user__id__exact", "object_id__exact")

        user_model = get_user_model()
        user_field_names = {f.name for f in user_model._meta.get_fields() if isinstance(f, models.Field)}
        for cand in ("username", "email", "nickname", "name"):
            if cand in user_field_names:
                fields.append(f"user__{cand}")  # 텍스트는 icontains

        return tuple(fields)

    def target_str(self, obj):
        base = f"{obj.content_type.app_label}.{obj.content_type.model}:{obj.object_id}"
        if obj.content_type.model in ("post", "comment"):
            return f"{base} (b64={id_to_public(obj.object_id)})"
        return base

    target_str.short_description = "대상"
