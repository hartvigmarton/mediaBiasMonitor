import datetime
from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from tinymce.models import HTMLField


class Article(models.Model):
    title = models.CharField(max_length=100)
    term = models.CharField(max_length=100)
    website = models.CharField(max_length=100)
    link = models.CharField(max_length=150)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @staticmethod
    def get_all_articles():
        return Article.objects.all()


class Meta:
    verbose_name = "Article"
    verbose_name_plural = "Articles"


class Blog_Post(models.Model):
    title = models.CharField(max_length=200)
   #content = models.TextField(max_length=100000)
    content = HTMLField()
    #content = RichTextUploadingField()
    pub_date = models.DateTimeField(auto_now_add=True)
