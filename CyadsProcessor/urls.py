"""CyadsProcessor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from processor import views as processor_views

from messaging.subscribers.batch_subscriber import BatchSubscriber
from processor.views import process, process_all, test, test_error
from ad_extension_pull.views import view_process_videos_collected_from_extension

router = routers.DefaultRouter()
# Register BatchViewSet to for prefix /api/batches/ to handle all API requests about batches
router.register(r'batches', processor_views.BatchViewSet)


urlpatterns = [
    path('', include('dashboard.urls')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path("batch/<int:batch_id>/process/", process, kwargs={'force': False}, name="process"),
    path("batch/<int:batch_id>/reprocess/", process, kwargs={'force': True}, name="reprocess"),
    path("process_all/", process_all, name="process_all"),
    path("test/<int:number>/", test, name="test"),
    path("test/error/<str:err_msg>", test_error, name="test_error"),
    path("ad_extension_process_videos", view_process_videos_collected_from_extension, name="ad_extension_video_process"),
    url('^api/', include(router.urls)),
]

subscriber = BatchSubscriber(os.getenv("GOOGLE_PROJECT_ID"),
                                     os.getenv("GOOGLE_TOPIC"),
                                     os.getenv("TOPIC_SUBSCRIPTION_NAME"))

subscriber.subscribe_topic()
