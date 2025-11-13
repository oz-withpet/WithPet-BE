# apps/community/reports/admin.py
from django import forms  # NEW
from django.contrib import admin, messages  # CHANGED: messages 사용
from django.contrib.contenttypes.models import ContentType  # NEW
from django.db import IntegrityError  # NEW

from .models import Report, REPORT_REASON_CHOICES
from apps.community.posts.models import Post  # NEW: 신고 대상은 Post만
from apps.community.common import validate_report, id_to_public  # NEW

# NEW: 관리자 폼 - 대상 Post를 명시적으로 선택, OTHER 5자 검증
class ReportAdminForm(forms.ModelForm):
    post = forms.ModelChoiceField(
        queryset=Post.objects.all(),
        required=True,
        label="대상 게시글",
        help_text="신고할 게시글을 선택하세요.",
    )
    # 모델의 reason(CharField + choices)을 그대로 사용하되, 라벨은 choices로 표시됨(저장은 코드)
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
        # 스펙: OTHER이면 detail 5자 이상 필수
        validate_report(code, detail)
        return cleaned

    def save(self, commit=True):
        # Post만 허용: content_type/object_id 세팅
        instance = super().save(commit=False)
        instance.content_type = ContentType.objects.get_for_model(Post)
        instance.object_id = self.cleaned_data["post"].pk
        if commit:
            instance.save()
        return instance


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    form = ReportAdminForm  # NEW: 커스텀 폼 적용

    # CHANGED: 대상 포스트를 사람이 읽기 쉽게 표시
    list_display = ("id", "user", "post_link", "reason", "status", "created_at")
    list_filter  = ("reason", "status", "created_at")
    search_fields = ("id", "user__username", "user__email", "detail")  # CHANGED: email도 검색

    readonly_fields = ("created_at",)

    # NEW: 대상 포스트 링크(공개 ID 병행 표기)
    def post_link(self, obj: Report):
        try:
            pub = id_to_public(obj.object_id)
        except Exception:
            pub = "?"
        return f"Post #{obj.object_id} (public_id={pub})"
    post_link.short_description = "대상 포스트"

    # NEW: (user, content_type, object_id) 유니크 위반 → 중복 신고 메시지
    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except IntegrityError:
            self.message_user(request, "이미 해당 게시글을 신고했습니다.", level=messages.ERROR)
