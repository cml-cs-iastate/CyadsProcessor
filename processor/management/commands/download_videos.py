from django.core.management.base import BaseCommand, CommandError
from processor.models import Videos, Channels, CheckStatus, Categories
from downloader.tasks import record_download_video, DuplicateVideoError
from django.db.models.functions import Length

import os

class Command(BaseCommand):
    help = 'Downloads videos that are not downloaded yets'

    def add_arguments(self, parser):
        pass
        #parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):    # Only download youtube videos
        # Only download ads
        download_dir = os.environ("AD_ARCHIVE_FILESTORE_DIR")
        assert download_dir is not None

        youtube_urls = Videos.objects.annotate(url_len=Length("url")).filter(url_len=11, watched_as_ad__gte=1,
                                                                             checked=False)

        vid: Videos
        for vid in youtube_urls:
            try:
                record_download_video(vid.url, download_dir)
                vid.save()
                print(f"downloaded ad to: {vid.AdFile_ID.ad_filepath} for video: {vid.url}")
            except Exception as e:
                print(f"Got error while downloading video {vid.url}: {e}")
        self.stdout.write(self.style.SUCCESS("Downloaded ads"))
