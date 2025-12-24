from django.db import models
from django.contrib.auth.models import User


class UserTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    essay_title = models.CharField(max_length=255)
    essay_text = models.TextField()

    score = models.FloatField(default=0)
    grammar_errors = models.IntegerField(default=0)
    spelling_errors = models.IntegerField(default=0)
    total_errors = models.IntegerField(default=0)
    word_count = models.IntegerField(default=0)

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.essay_title} ({self.score})"
