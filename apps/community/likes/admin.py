from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from .models import Like
from apps.community.common import id_to_public, id_from_public


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "target_str", "created_at")
    list_filter = ("content_type", "created_at")
    search_fields: tuple[str, ...] = ("content_type__model",)

    raw_id_fields = ("user",)
    date_hierarchy = "created_at"
    ordering = ("-created_at", "-id")
    list_select_related = ("user", "content_type")
    readonly_fields = ("created_at",)
    fields = ("user", "content_type", "object_id", "created_at")

    def get_search_fields(self, request):
        fields = list(self.search_fields)
        user_model = get_user_model()
        user_field_names = {
            f.name for f in user_model._meta.get_fields() if isinstance(f, models.Field)
        }
        for cand in ("username", "email", "nickname", "name"):
            if cand in user_field_names:
                fields.append(f"user__{cand}")  # icontains
        seen = set()
        fields = [f for f in fields if not (f in seen or seen.add(f))]
        return tuple(fields)

    def get_search_results(self, request, queryset, search_term):
        qs, use_distinct = super().get_search_results(request, queryset, search_term)
        term = (search_term or "").strip()

        extra_q = queryset.none()

        if term.isdigit():
            num = int(term)
            extra_q = queryset.filter(Q(object_id=num) | Q(user__id=num))

        else:
            try:
                pk_from_b64 = id_from_public(term)
                extra_q = queryset.filter(object_id=pk_from_b64)
            except Exception:
                pass

        if extra_q.exists():
            qs = (qs | extra_q).distinct()
            use_distinct = True or use_distinct

        return qs, use_distinct

    def target_str(self, obj):
        base = f"{obj.content_type.app_label}.{obj.content_type.model}:{obj.object_id}"
        if obj.content_type.model in ("post", "comment"):
            return f"{base} (b64={id_to_public(obj.object_id)})"
        return base

    target_str.short_description = "대상"
