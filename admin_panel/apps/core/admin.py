from django.contrib import admin
from .models import User, Job, Application


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "full_name", "email", "role", "company_name", "is_active", "created_at"]
    list_filter = ["role", "is_active"]
    search_fields = ["email", "full_name", "company_name"]
    list_editable = ["is_active"]
    readonly_fields = ["hashed_password", "created_at"]
    ordering = ["-created_at"]


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "employer", "location", "job_type", "status", "created_at"]
    list_filter = ["status", "job_type"]
    search_fields = ["title", "skills_required", "location"]
    list_editable = ["status"]
    ordering = ["-created_at"]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["id", "candidate", "job", "ats_score", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["candidate__full_name", "job__title"]
    list_editable = ["status"]
    ordering = ["-ats_score"]
    readonly_fields = ["ats_score", "resume_path", "created_at"]