from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone_number = models.CharField(max_length=11, blank=True, null=True)
    biography = models.TextField(max_length=500, blank=True, null=True)
    job = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='images/', blank=True, null=True)
