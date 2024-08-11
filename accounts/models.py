from django.contrib.auth.models import User
from django.db import models

class CommonProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='common_profile')
    name = models.CharField(max_length=20, unique=True)