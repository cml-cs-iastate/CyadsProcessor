from celery import shared_task

import logging

import youtube_dl
from processor.models import Videos, AdFile, CheckStatus, CollectionType
from django.db.models.functions import Length

from pathlib import PurePosixPath, Path
from urllib.parse import unquote, urlparse
import re

logger = logging.getLogger(__name__)



@shared_task(acks_late=True, name="tasks.cyads_video_download")
def download_videos_from_db():
    try:
        # Only download youtube videos
        youtube_urls = Videos.objects.annotate(url_len=Length("url")).filter(url_len=11)

        vid: Videos
        for vid in youtube_urls:
            full_url = f"https://www.youtube.com/embed/{vid.url}?rel=0&hl=en&cc_lang_pref=en"

            # Exception raised if unique constrain violated
            adfile = AdFile(collection_type=CollectionType.CYADS)

            video_download(adfile, full_url)
            vid.AdFile_ID = adfile
            # Only save if no errors
            adfile.save()
            vid.checked = True
            vid.check_status = CheckStatus.FOUND
            vid.save()
    except Exception as e:
        logger.exception(f"Got error while downloading video: {e} ")


def video_download(adfile: AdFile, url: str):
    """Download video from ad url"""

    class MyLogger:
        def debug(self, msg):
            print(msg)
            match = re.search('ffmpeg..* Merging formats into \"(.*)\"$', msg)
            if match:
                final_path = match.group(1)
                name = Path(final_path).name

                # This log msg occurs after any status messages from youtube-dl
                # This field will not be updated again for a video download.
                adfile.ad_filepath = name

        def warning(self, msg):
            pass

        def error(self, msg):
            print(msg)

    def my_hook(d):
        if d["status"] == "finished":
            try:
                # downloaded_bytes presence indicates video was downloaded and not skipped
                # due to file existing
                d["downloaded_bytes"]
            except KeyError:
                print("File already exists")
                print(d["filename"])
                raise Exception("key assumption violated. external ad networks use unique ids on same domain")

            print("File did not exist")
            print(d["filename"])
            downloaded_filepath = Path(d["filename"])
            # Only store name of file
            filename = downloaded_filepath.name
            print(filename)
            adfile.ad_filepath = filename

    ydl_opts = {
        # Pick best audio and video format and combine them OR pick the file with the best combination
        # Need to capture filename of merged ffmpeg file
        # Best doesn't return the highest video, only the highest pair.
        # So 360p video may have the highest audio
        #'format': 'best',
        #'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=webm]+bestaudio[ext=webm]/best',
        'format': 'bestvideo+bestaudio/best',
        'nooverwrites': False,
        'continuedl': True,
        'progress_hooks': [my_hook],
        'logger': MyLogger(),
    }

    # Set collection dir
    if adfile.collection_type == CollectionType.CYADS:
        collection_dir = "CyAds"
    else:
        collection_dir = "GoogleTReport"
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # Extract info about video to determine where to download the file to
        result = ydl.extract_info(url, download=False)
        extractor = result["extractor"]

        if extractor == "generic":
            filename = PurePosixPath(unquote(urlparse(url).path)).parts[3]
            ydl_opts["outtmpl"] = f'ads/{collection_dir}/{filename}.%(ext)s'

        elif extractor == "youtube":
            ydl_opts["outtmpl"] = f'ads/{collection_dir}/%(id)s.%(ext)s'
            print(extractor)

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


