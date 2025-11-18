from django import forms  # NEW
from django.contrib import admin, messages  # CHANGED: messages 사용
from django.contrib.contenttypes.models import ContentType  # NEW
from django.db import IntegrityError  # NEW

from .models import Report, REPORT_REASON_CHOICES
from apps.community.posts.models import Post  # NEW: 신고 대상은 Post만
from apps.community.common import validate_report  # NEW

class ReportAdminForm(forms.ModelForm):
    post = forms.ModelChoiceField(
        queryset=Post.objects.all(),
        required=True,
        label="대상 게시글",
        help_text="신고할 게시글을 선택하세요.",
    )
    reason = forms.ChoiceField(choices=REPORT_REASON_CHOICES, label="신고 사유")
    detail = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label="상세 사유",
        help_text="사유가 '기타'인 경우 5자 이상 입력 필요",
    )

    class Meta:
        model = Report
        fields = ("user", "post", "reason", "detail", "status")

    def clean(self):
        cleaned = super().clean()
        code = cleaned.get("reason") or ""
        detail = cleaned.get("detail") or ""
        validate_report(code, detail)
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.content_type = ContentType.objects.get_for_model(Post)
        instance.object_id = self.cleaned_data["post"].pk
        if commit:
            instance.save()
        return instance


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    form = ReportAdminForm

    list_display = ("id", "user", "post_link", "reason", "status", "created_at")
    list_filter  = ("reason", "status", "created_at")
    search_fields = ("id", "user__username", "user__email", "detail")  # CHANGED: email도 검색

    readonly_fields = ("created_at",)

    def post_link(self, obj: Report):
        try:
            pub = int(obj.object_id)
        except Exception:
            pub = "?"
        return f"Post #{obj.object_id} (public_id={pub})"
    post_link.short_description = "대상 포스트"

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except IntegrityError:
            self.message_user(request, "이미 해당 게시글을 신고했습니다.", level=messages.ERROR)
