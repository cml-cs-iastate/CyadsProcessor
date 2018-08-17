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

urlpatterns = [
    path('', include('dashboard.urls')),
    path('admin/', admin.site.urls),
]

subscriber = BatchSubscriber(os.getenv("GOOGLE_PROJECT_ID"),
                                     os.getenv("GOOGLE_TOPIC"),
                                     os.getenv("TOPIC_SUBSCRIPTION_NAME"))
subscriber.subscribe_topic()
