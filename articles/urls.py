from django.urls import path
from . import views


urlpatterns = [
    path('graph/', views.total_nr_titles_per_medium_graph, name='total_nr_titles_per_medium_graph'),
    path('blog/<slug:slug>/', views.blog_post_detail, name='blog_post_detail'),
    path('titles/', views.view_titles, name='view_titles'),

]
