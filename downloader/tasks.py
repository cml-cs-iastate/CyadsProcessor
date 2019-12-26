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
    # Only download youtube videos
    # Only download ads
    youtube_urls = Videos.objects.annotate(url_len=Length("url")).filter(url_len=11, watched_as_ad__gte=1,
                                                                         checked=False)

    vid: Videos
    for vid in youtube_urls:
        try:
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
            logger.exception(f"Got error while downloading video {full_url}: {e}")


class DuplicateVideoError(Exception):
    """A video is already downloaded by youtube-dl"""

    def __init__(self, message, url: str = None, path: Path = None):
        self.message = message
        self.url: str = url
        self.path: Path = path

    def __str__(self):
        return f"{self.message}: url={self.url}, path={self.path}"


class MissingVideoError(Exception):
    """A video is no longer available to download"""

    def __init__(self, message, url: str = None):
        self.message = message
        self.url: str = url

    def __str__(self):
        return f"{self.message}: url={self.url}"


def video_download(adfile: AdFile, url: str, download_dir: str):
    """Download video from ad url"""

    class MyLogger:
        def debug(self, msg):
            print(msg)
            already_downloaded_match = re.search("\[download\] (.*) has already been.*", msg)
            if already_downloaded_match:
                filepath = already_downloaded_match.group(1)
                raise DuplicateVideoError("key assumption violated. external ad networks use unique ids on same domain",
                                          url=url, path=filepath)

            new_download_match = re.search('Merging formats into \"(.*)\"$', msg)
            if new_download_match:
                final_path = new_download_match.group(1)

                # This log msg occurs after any status messages from youtube-dl
                # This field will not be updated again for a video download.
                adfile.ad_filepath = Path(final_path).relative_to(download_dir).as_posix()

        def warning(self, msg):
            print(msg)

        def error(self, msg):
            print(msg)

        def info(self, msg):
            print(msg)

    def my_hook(d):
        pass

    ydl_opts = {
        # Pick best audio and video format and combine them OR pick the file with the best combination
        # Need to capture filename of merged ffmpeg file
        # Best doesn't return the highest video, only the highest pair.
        # So 360p video may have the highest audio
        # 'format': 'best',
        # 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=webm]+bestaudio[ext=webm]/best',
        'format': 'bestvideo+bestaudio/best',
        'nooverwrites': True,
        # 'continuedl': True,
        'progress_hooks': [my_hook],
        'logger': MyLogger(),
    }

    # Set collection dir
    if adfile.collection_type == CollectionType.CYADS.value:
        collection_dir = "CyAds"
    elif adfile.collection_type == CollectionType.GOOGLETREPORT.value:
        collection_dir = "GoogleTReport"
    else:
        raise ValueError(f"Unknown CollectionType: {adfile.collection_type}")

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # Extract info about video to determine where to download the file to
        try:
            result = ydl.extract_info(url, download=False)
        except youtube_dl.utils.DownloadError as e:
            if "video is unavailable" in e.args[0]:
                raise MissingVideoError("Missing video", url=url) from e
            else:
                raise e
        extractor = result["extractor"]

        base = Path(download_dir).joinpath(collection_dir).as_posix()
        if extractor == "generic":
            filename = PurePosixPath(unquote(urlparse(url).path)).parts[3]
            ydl_opts["outtmpl"] = base + f'/{filename}.%(ext)s'
        elif extractor == "youtube":
            ydl_opts["outtmpl"] = base + f'/%(id)s.%(ext)s'
            print(extractor)

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def record_download_video(url: str, download_dir: str):
    """Download and record the video given by `url`"""
    adfile = AdFile()
    adfile.collection_type = CollectionType.CYADS.value
    try:
        video_download(adfile, url, download_dir)
        adfile.save()
        vid = Videos.objects.get(url=url)
        vid.checked = True
        vid.check_status = CheckStatus.FOUND.value
        vid.AdFile_ID = adfile
        vid.save()
        return vid
    except MissingVideoError:
        vid: Videos = Videos.objects.missing(vid_url=url)
        vid.checked = True
        vid.check_status = CheckStatus.MISSING.value
        vid.save()
        return vid
    except DuplicateVideoError as e:
        # Maybe notify of video not downloading somehow?
        print(e)
        raise e
