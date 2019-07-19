from .tasks import download_videos_from_db


class DownloadProcessor:

    def get(self, request):
        print(request)
        download_videos_from_db.delay()
        return 200

    def post(self, request):
        download_videos_from_db.delay()
        return 200


