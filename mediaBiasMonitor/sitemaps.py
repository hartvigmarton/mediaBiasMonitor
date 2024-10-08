from django.contrib.sitemaps import Sitemap
from articles.models import Blog_Post
from django.urls import reverse


class BlogPostSitemap(Sitemap):
    def items(self):
        return Blog_Post.objects.all()

    def lastmod(self, obj):
        return obj.pub_date

class StaticViewSitemap(Sitemap):

    def items(self):
        return ["index", "list_blog_posts"]

    def location(self, item):
        return reverse(item)



