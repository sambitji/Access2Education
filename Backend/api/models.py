from django.db import models
from django.utils import timezone

class User(models.Model):
    name = models.CharField(max_length=60)
    email = models.EmailField(max_length=100, unique=True, db_index=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=20, default="student")
    avatar_url = models.CharField(max_length=255, default="", blank=True)
    learning_style = models.CharField(max_length=50, null=True, blank=True)
    cluster_id = models.IntegerField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    total_completed = models.IntegerField(default=0)
    joined_at = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.name} ({self.email})"


class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    scores = models.JSONField()  # Store dictionary of category scores
    cluster = models.IntegerField()
    learning_style = models.CharField(max_length=50)
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'test_results'

    def __str__(self):
        return f"TestResult for {self.user.name} at {self.submitted_at}"


class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    content_id = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    completed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'progress'
        unique_together = ('user', 'content_id')
        indexes = [
            models.Index(fields=['user', 'content_id'], name='idx_progress_user_content'),
        ]

    def __str__(self):
        return f"Progress {self.content_id} - User {self.user_id} ({self.completed})"


class SRCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sr_cards')
    concept_id = models.CharField(max_length=100)
    concept_title = models.CharField(max_length=255)
    subject = models.CharField(max_length=50)
    interval = models.IntegerField(default=0)
    easiness = models.FloatField(default=2.5)
    repetition = models.IntegerField(default=0)
    next_review = models.DateTimeField(default=timezone.now)
    learning_style = models.IntegerField(default=0)

    class Meta:
        db_table = 'sr_cards'
        unique_together = ('user', 'concept_id')
        indexes = [
            models.Index(fields=['user', 'concept_id'], name='idx_sr_user_concept'),
        ]

    def __str__(self):
        return f"SRCard {self.concept_id} for {self.user.name}"


class RefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.CharField(max_length=512, unique=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'refresh_tokens'

    def __str__(self):
        return f"RefreshToken for {self.user.name}"


class OTP(models.Model):
    email = models.EmailField(max_length=100, db_index=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = 'otps'

    def __str__(self):
        return f"OTP for {self.email} ({self.otp})"


class SRReviewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sr_reviews')
    concept_id = models.CharField(max_length=100)
    quality = models.IntegerField()
    interval_after = models.IntegerField()
    easiness_after = models.FloatField()
    reviewed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'sr_review_history'

    def __str__(self):
        return f"SRReviewHistory {self.concept_id} - {self.user.name}"
