from django.contrib import admin

from .models import Article, Blog_Post

admin.site.register(Article)
@admin.register(Blog_Post)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date')  # Customize the fields displayed in the admin list view
    # You can customize the admin options further if needed.

