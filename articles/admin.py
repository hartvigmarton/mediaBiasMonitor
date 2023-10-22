from django.contrib import admin

from .models import Article, Update

admin.site.register(Article)
@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date')  # Customize the fields displayed in the admin list view
    # You can customize the admin options further if needed.