from django.db import models
from django.db.models import Q
from django.conf import settings
from apps.community.common import CATEGORY_KOR_ALLOWED, id_to_public

class PostCategory(models.Model):
    name = models.CharField(max_length=20, unique=True)
    class Meta:
        db_table = "post_category"
        constraints = [
            models.CheckConstraint(
                check=Q(name__in=CATEGORY_KOR_ALLOWED),
                name="post_category_name_allowed_only",
            )
        ]

    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="posts")
    title = models.CharField(max_length=100)      # 제목 ≤ 100
    content = models.TextField()                  # 본문 ≤ 20000 (Serializer에서 길이 검증)
    category = models.ForeignKey(PostCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name="posts")
    image = models.ImageField(upload_to="posts/%Y/%m/", null=True, blank=True)

    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "post"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["-view_count"]),
            models.Index(fields=["-like_count"]),
            models.Index(fields=["category", "-created_at"]),
        ]

    @property
    def public_id(self) -> str:
        return id_to_public(self.id)

    def __str__(self):
        return f"[{self.id}] {self.title}"
