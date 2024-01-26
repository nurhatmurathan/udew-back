from django.contrib.auth.models import User
from django.db import models

# class Project(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     name = models.CharField()


class MultilingualText(models.Model):
    en = models.TextField()
    ru = models.TextField()
    kz = models.TextField()


class ImageUrls(models.Model):
    preview = models.URLField(max_length=200)
    pc = models.URLField(max_length=200)
    tablet = models.URLField(max_length=200)
    modile = models.URLField(max_length=200)
