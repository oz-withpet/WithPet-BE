# apps/community/reports/repositories.py
from typing import Any
from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.db.models import Model

from .models import Report


class DuplicateReportError(Exception):
    """동일 (user, content_type, object_id) 신고 중복."""
    pass


class TargetNotFoundError(Exception):
    """신고 대상(Post)을 찾을 수 없음."""
    pass


def resolve_post_model() -> Any:
    """
    Post 모델을 안전하게 찾는다.
    - 우선 settings.COMMUNITY_POST_MODEL = "app_label.ModelName" 지원
    - 없으면 흔한 후보들을 순차 탐색
    """
    label = getattr(settings, "COMMUNITY_POST_MODEL", None)
    if label and isinstance(label, str) and "." in label:
        app_label, model_name = label.split(".", 1)
        model = django_apps.get_model(app_label, model_name)
        if model is not None:
            return model

    for candidate in ("posts.Post", "post.Post", "community_posts.Post", "community.Post"):
        app_label, model_name = candidate.split(".", 1)
        model = django_apps.get_model(app_label, model_name)
        if model is not None:
            return model

    raise LookupError(
        "Post 모델을 찾지 못했습니다. settings.COMMUNITY_POST_MODEL='app_label.ModelName' 을 설정하세요."
    )


class ReportRepository:
    @staticmethod
    def get_post_or_404(pk: int) -> Model:
        post_model = resolve_post_model()
        try:
            return post_model.objects.get(pk=pk)
        except post_model.DoesNotExist:  # type: ignore[attr-defined]
            raise TargetNotFoundError()

    @staticmethod
    def create_for_post(user, post: Model, reason_code: str, detail: str) -> Report:
        content_type = ContentType.objects.get_for_model(post, for_concrete_model=False)
        try:
            report = Report.objects.create(
                user=user,
                content_type=content_type,
                object_id=post.pk,
                reason=reason_code,
                detail=detail or "",
            )
        except IntegrityError:
            # models.UniqueConstraint("user", "content_type", "object_id") 위반
            raise DuplicateReportError()
        return report
