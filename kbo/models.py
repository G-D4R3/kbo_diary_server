from django.db import models

# Create your models here.
class Team(models.Model):
    full_name = models.CharField(max_length=20)
    name = models.CharField(max_length=10)
    logo = models.ImageField(upload_to='team_logos/', null=True)
    initial_logo = models.ImageField(upload_to='team_initial_logos/', null=True)