from django.contrib import admin
from .models import User, TestResult, Progress, SRCard, RefreshToken, OTP, SRReviewHistory

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'role', 'learning_style', 'is_verified', 'joined_at')
    search_fields = ('name', 'email')
    list_filter = ('role', 'learning_style', 'is_verified')

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'learning_style', 'cluster', 'submitted_at')
    search_fields = ('user__name', 'user__email', 'learning_style')
    list_filter = ('learning_style', 'cluster')

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_id', 'subject', 'completed', 'score', 'last_accessed')
    search_fields = ('user__name', 'user__email', 'content_id', 'subject')
    list_filter = ('completed', 'subject')

@admin.register(SRCard)
class SRCardAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'concept_id', 'concept_title', 'subject', 'interval', 'easiness', 'next_review')
    search_fields = ('user__name', 'concept_title', 'concept_id')
    list_filter = ('subject', 'interval')

@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'expires_at')
    search_fields = ('user__name', 'user__email')

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'otp', 'expires_at', 'used')
    search_fields = ('email', 'otp')
    list_filter = ('used',)

@admin.register(SRReviewHistory)
class SRReviewHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'concept_id', 'quality', 'interval_after', 'reviewed_at')
    search_fields = ('user__name', 'concept_id')
    list_filter = ('quality',)
