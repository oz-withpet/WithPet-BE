from django.db import models
from django.conf import settings
from apps.community.common import id_to_public

class Comment(models.Model):
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="comments", db_index=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="comments")
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")

    content = models.TextField()

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "community_comment"
        indexes = [
            models.Index(fields=["post", "-created_at"]),
        ]

    @property
    def public_id(self) -> str:
        return id_to_public(self.id)

    def __str__(self):
        return f"Comment({self.id}) on Post({self.post_id})"

    def clean(self):
        if self.parent and self.parent.post_id != self.post_id:
            from django.core.exceptions import ValidationError
            raise ValidationError("부모 댓글은 동일한 게시글에 속해야 합니다.")
