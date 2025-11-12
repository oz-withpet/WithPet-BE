# apps/community/reports/admin.py
from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "content_type", "object_id", "reason", "status", "created_at")
    list_filter = ("reason", "status", "created_at")
    search_fields = ("id", "user__username", "detail")
