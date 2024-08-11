from django.db import models

# Create your models here.
class Team(models.Model):
    full_name = models.CharField(max_length=20)
    name = models.CharField(max_length=10)
    # image = models.ImageField(upload_to=product_image_path)