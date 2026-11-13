
from django.conf import settings
from django.db import models


class SavedRepository(models.Model):
    # Link each saved repository to its user
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_repositories'
    )

    github_id = models.BigIntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.URLField()
    language = models.CharField(max_length=100, blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent duplicate saves for the same user
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'github_id'],
                name='unique_user_github_repo'
            )
        ]

    def __str__(self):
        return self.name

