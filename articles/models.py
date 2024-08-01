import datetime
from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from tinymce.models import HTMLField
from django.utils.text import slugify
from django.db.models.signals import pre_save


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
    slug = models.SlugField(max_length=200, unique=True)
    content = HTMLField()
    pub_date = models.DateTimeField(auto_now_add=True)
def pre_save_blog_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)

pre_save.connect(pre_save_blog_post_receiver, sender=Blog_Post)


