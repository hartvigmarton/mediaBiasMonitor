from django.urls import path

from . import views
from .views import ArticleList


urlpatterns = [
    path("", views.index, name="index"),
    path('graph/', views.graph_view, name='graph_view'),
    path('graph2/', views.graph_view2, name='graph_view2'),
    #path('graph/', views.ArticleList.as_view(), name='article-list'),
    path('entry_list/', views.list_entries, name='list_entries'),
    #path('start_periodic_task/', views.start_periodic_task, name='start_periodic_task'),
    path('titles/', views.view_titles, name='view_titles'),
    #path('articles/', views.view_articles, name='view_articles'),

]
