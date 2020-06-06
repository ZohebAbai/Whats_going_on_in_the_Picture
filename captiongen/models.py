from django.db import models

# Create your models here.
class PicUpload(models.Model):
    imagefile = models.ImageField(upload_to = 'images', blank=True)
