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
from django.contrib import admin
from django.urls import path, include

from messaging.subscribers.batch_subscriber import BatchSubscriber
from downloader.download import DownloadProcessor
import downloader
from downloader import views
from processor.views import process, process_all, test
from ad_extension_pull.views import process_videos_collected_from_extension

urlpatterns = [
    path('', include('dashboard.urls')),
    path('admin/', admin.site.urls),
    path("batch/<int:batch_id>/process/", process, kwargs={'force': False}, name="process"),
    path("batch/<int:batch_id>/reprocess/", process, kwargs={'force': True}, name="reprocess"),
    path("process_all/", process_all, name="process_all"),
    path("test/<int:number>/", test, name="test"),
    path("ad_extension_process_videos", process_videos_collected_from_extension, name="ad_extension_video_process"),
]


subscriber = BatchSubscriber(os.getenv("GOOGLE_PROJECT_ID"),
                                     os.getenv("GOOGLE_TOPIC"),
                                     os.getenv("TOPIC_SUBSCRIPTION_NAME"))

subscriber.subscribe_topic()
