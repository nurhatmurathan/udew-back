from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Token(models.Model):
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super(Token, self).save(*args, **kwargs)


class Code(models.Model):
    code = models.PositiveIntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super(Code, self).save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(default=None, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    children = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=55, null=True, blank=True)
    body_mass_index = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    smoker = models.CharField(max_length=10, null=True, blank=True)
    region = models.CharField(max_length=20, null=True, blank=True)
    charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    iin = models.CharField(max_length=11, unique=True, null=True, blank=True)
    is_email_confirmed = models.BooleanField(default=False)
    email_confirm_date = models.DateTimeField(null=True, blank=True)
    confirmation_token = models.OneToOneField(Token, null=True, blank=True, on_delete=models.SET_NULL)
    chat_thread_id = models.CharField(null=True)


class MultilingualText(models.Model):
    en = models.TextField()
    ru = models.TextField()
    kz = models.TextField()


class ImageUrls(models.Model):
    preview = models.URLField(max_length=200)
    pc = models.URLField(max_length=200)
    tablet = models.URLField(max_length=200)
    mobile = models.URLField(max_length=200)


class ApplicationCompensation(models.Model):
    class Status(models.TextChoices):
        APPROVED = "APPROVED", "approved"
        NOT_APPROVED = "NOT_APPROVED", "not approved"
        NOT_CONSIDERED = "NOT_CONSIDERED", "not considered"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    statement = models.TextField()
    iin = models.CharField()
    policy_number = models.CharField(default=None, null=True, blank=True)
    medical_documents = models.URLField()
    status = models.CharField(max_length=25, choices=Status.choices, default=Status.NOT_CONSIDERED)


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=255)
    content = models.TextField()


# class Chat(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=255)
#     messages = models.ManyToManyField(Message)


# class ChatImages(models.Model):
#     image = models.CharField(max_length=)
