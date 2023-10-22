from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('update_list/', views.list_updates, name='list_updates'),
    path('start_periodic_task/', views.start_periodic_task, name='start_periodic_task'),
    path('output/', views.get_terms_on_sites, name='get_terms_on_sites'),
    path('articles/', views.update_database, name='update_database'),

]