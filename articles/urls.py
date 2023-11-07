from django.urls import path

from . import views
from .views import ArticleList

urlpatterns = [
    path("rss_titles",views.rss_test,name="rss_test"),
    path("", views.index, name="index"),
    path('graph/', views.ArticleList.as_view(), name='article-list'),
    path('entry_list/', views.list_entries, name='list_entries'),
    path('start_periodic_task/', views.start_periodic_task, name='start_periodic_task'),
    path('output/', views.get_terms_on_sites, name='get_terms_on_sites'),
   # path('articles/', views.update_database, name='update_database'),

]