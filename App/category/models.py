from django.db import models
from django.urls import reverse

from cloudinary.models import CloudinaryField



class Category(models.Model):
    category_name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    category_img = CloudinaryField('category_image', blank=True, null=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('category_list_slug', args=[self.slug])

    def __str__(self):
        return self.category_name