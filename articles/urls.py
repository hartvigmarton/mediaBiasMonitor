from django.urls import path
from . import views


urlpatterns = [
    path('graph/', views.graph_view, name='graph_view'),
    path('blog/<slug:slug>/', views.blog_post_detail, name='blog_post_detail'),
    path('titles/', views.view_titles, name='view_titles'),

]
