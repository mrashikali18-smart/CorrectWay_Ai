"""
Database models for CorrectWay.

Rewritten from the original Mongoose schemas:

  server/models/User.js
    -> Django's built-in auth.User already covers name/email/password.
       `Profile` below adds the one extra field the original had
       (`role: "student" | "admin"`) as a one-to-one extension, since
       Django's User model is not meant to be edited directly.

  server/models/QuizResult.js
    -> `QuizResult` below, field-for-field equivalent:
         user            -> user (FK, nullable for anonymous/offline results)
         answers (Map)   -> answers (JSONField)
         topMatches      -> top_matches (JSONField, list of {title, tool, pct})
         categoryScores  -> category_scores (JSONField)
         varietyPreference -> variety_preference (BooleanField)
         timestamps      -> created_at (DateTimeField, auto_now_add)
"""
from django.conf import settings
from django.db import models


class Profile(models.Model):
    STUDENT = "student"
    ADMIN = "admin"
    ROLE_CHOICES = [(STUDENT, "Student"), (ADMIN, "Admin")]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)

    def __str__(self):
        return f"{self.user.email} ({self.role})"


class QuizResult(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_results",
        null=True,
        blank=True,
    )
    answers = models.JSONField(help_text="Map of questionId -> yes/no (true/false)")
    top_matches = models.JSONField(
        default=list, help_text="Ranked list of {title, tool, pct} career matches"
    )
    category_scores = models.JSONField(
        default=dict, help_text="Map of category code -> score"
    )
    variety_preference = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        who = self.user.email if self.user_id else "anonymous"
        return f"QuizResult({who}, {self.created_at:%Y-%m-%d %H:%M})"


class ContactMessage(models.Model):
    """Messages submitted through the public Contact page."""

    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}> — {self.created_at:%Y-%m-%d %H:%M}"
