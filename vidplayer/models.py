from django.db import models
from django.utils.text import slugify
from autoslug import AutoSlugField

# Create your models here.

class Videos(models.Model):
    title = models.CharField(max_length=50, null = True)
    video = models.FileField( upload_to='videos/', null = True)
    slug =AutoSlugField(unique=True, populate_from='title', null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)


    def save(self, *args, **kwargs):
       if not self.slug:
           self.slug=slugify(self.title)
       super().save(*args, **kwargs) 

    def __str__(self):
        return self.title

