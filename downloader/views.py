from django.shortcuts import render

# Create your views here.


from .tasks import download_videos_from_db
from django.http import HttpResponse


def download(request):
        print(request)
        download_videos_from_db.delay()
        return HttpResponse("queued video download")


