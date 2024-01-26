from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Token(models.Model):
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=1)
        super(Token, self).save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    confirmation_token = models.OneToOneField(Token, null=True, blank=True, on_delete=models.SET_NULL)
