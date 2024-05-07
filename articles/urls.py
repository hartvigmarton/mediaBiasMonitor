from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path('<int:post_id>/', views.blog_post_detail, name='blog_post_detail'),
    path('graph/', views.graph_view, name='graph_view'),
    path('graph3/',views.index_graph,name='index-graph'),
    path('blog/<int:post_id>/', views.blog_post_detail, name='blog_post_detail'),
    path('entry_list/', views.list_blog_posts, name='list_blog_posts'),
    path('titles/', views.view_titles, name='view_titles'),

]
