
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.running, name='index'),
    path('completed.html', views.completed),
    path('running.html', views.running),
    path('database_mb.html', views.database_mb_view),
]
