import logging

from typing import Optional

import youtube_dl
from processor.models import Videos, AdFile, CheckStatus, CollectionType

from pathlib import PurePosixPath, Path
from urllib.parse import unquote, urlparse
import re

logger = logging.getLogger(__name__)


class DuplicateVideoError(Exception):
    """A video is already downloaded by youtube-dl"""

    def __init__(self, message, url: str = None, path: Path = None):
        self.message = message
        self.url: str = url
        self.path: Path = path

    def __str__(self):
        return f"{self.message}: url={self.url}, path={self.path}"


class MissingVideoError(Exception):
    """A video is no longer available to download because it is taken down"""

    def __init__(self, message, url: str = None):
        self.message = message
        self.url: str = url

    def __str__(self):
        return f"{self.message}: url={self.url}"


class PrivateVideoError(Exception):
    """A video is no longer available to download because it is private"""

    def __init__(self, message, url: str = None):
        self.message = message
        self.url: str = url

    def __str__(self):
        return f"{self.message}: url={self.url}"


class UserRemovedVideoError(Exception):
    """A video is no longer available to download because it was removed by the user"""

    def __init__(self, message, url: str = None):
        self.message = message
        self.url: str = url

    def __str__(self):
        return f"{self.message}: url={self.url}"


class AccountTerminationVideoError(Exception):
    """A video is no longer available to download because the associated account was terminated"""

    def __init__(self, message, url: str = None):
        self.message = message
        self.url: str = url

    def __str__(self):
        return f"{self.message}: url={self.url}"


def video_download(url: str, download_dir: str) -> Path:
    """Download video from ad url"""

    class MyLogger:
        def __init__(self):
            self.ad_filepath: Optional[Path] = None

        def debug(self, msg):
            print(msg)
            new_download_match = re.search('Merging formats into \"(.*)\"$', msg)
            already_downloaded_match = re.search("\[download\] (.*) has already been downloaded and merged.*", msg)
            if new_download_match:
                final_path = new_download_match.group(1)

                # This log msg occurs after any status messages from youtube-dl
                # This field will not be updated again for a video download.
                self.ad_filepath = Path(final_path)
                return
            elif already_downloaded_match:
                filepath = already_downloaded_match.group(1)
                self.ad_filepath = Path(filepath)
                return

        def warning(self, msg):
            print(msg)

        def error(self, msg):
            print(msg)

        def info(self, msg):
            print(msg)

    def my_hook(d):
        pass

    mylogger = MyLogger()

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
        'logger': mylogger,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # Extract info about video to determine where to download the file to
        try:
            result = ydl.extract_info(url, download=False)
        except youtube_dl.utils.DownloadError as e:
            if "video is unavailable" in e.args[0]:
                raise MissingVideoError("Missing video", url=url) from e
            elif "video is private" in e.args[0]:
                raise PrivateVideoError("Private video", url=url) from e
            elif "removed by the user" in e.args[0]:
                raise UserRemovedVideoError("User removed video", url=url) from e
            elif "account associated with this video has been terminated" in e.args[0]:
                raise AccountTerminationVideoError("Missing video due to account termination", url=url) from e
            else:
                raise e
        extractor = result["extractor"]

        if extractor == "generic":
            filename = PurePosixPath(unquote(urlparse(url).path)).parts[3]
            ydl_opts["outtmpl"] = download_dir + f'/{filename}.%(ext)s'
        elif extractor == "youtube":
            ydl_opts["outtmpl"] = download_dir + f'/%(id)s.%(ext)s'
            print(extractor)

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    saved_ad_filepath = mylogger.ad_filepath
    if saved_ad_filepath == download_dir:
        raise ValueError(f"`No video path was saved? Was the video downloaded?`, for url={url}")
    else:
        return saved_ad_filepath


def record_download_video(url: str, base_download_dir: str) -> Videos:
    """Download and record the video given by `url` Must be in db already"""
    vid = Videos.objects.get(url=url)

    collection_type = CollectionType.CYADS.value
    if collection_type == CollectionType.CYADS.value:
        collection_dir = "CyAds"
    elif collection_type == CollectionType.GOOGLETREPORT.value:
        collection_dir = "GoogleTReport"
    else:
        raise ValueError(f"Unknown CollectionType: {collection_type}")

    specific_collection_dir = Path(base_download_dir).joinpath(collection_dir)

    try:
        ad_filepath = video_download(url, specific_collection_dir.as_posix())
        if ad_filepath is None:
            raise DuplicateVideoError(f"Video already been downloaded", url=url)
        else:
            posix_ad_filepath = ad_filepath.relative_to(base_download_dir).as_posix()

        adfile, created = AdFile.objects.get_or_create(ad_filepath=posix_ad_filepath, collection_type=collection_type)

        # Don't update any existing ad file paths
        if created:
            adfile.ad_filepath = posix_ad_filepath
            adfile.collection_type = collection_type
        assert adfile.ad_filepath is not None and adfile.ad_filepath != ""
        vid.checked = True
        vid.check_status = CheckStatus.FOUND.value
        try:
            assert vid.AdFile_ID is None or vid.AdFile_ID == adfile.id
        except AssertionError:
            raise DuplicateVideoError(f"Attempt to change Adfile for vid={repr(vid)}")
        vid.AdFile_ID = adfile
        adfile.save()
        vid.save()
        return vid
    except MissingVideoError:
        vid: Videos = Videos.objects.filter(url=url).first()
        vid.checked = True
        vid.check_status = CheckStatus.MISSING.value
        vid.save()
        return vid
    except PrivateVideoError:
        vid: Videos = Videos.objects.filter(url=url).first()
        vid.checked = True
        vid.check_status = CheckStatus.PRIVATE.value
        vid.save()
        return vid
    except UserRemovedVideoError:
        vid: Videos = Videos.objects.filter(url=url).first()
        vid.checked = True
        vid.check_status = CheckStatus.USER_REMOVED.value
        vid.save()
        return vid
    except AccountTerminationVideoError:
        vid: Videos = Videos.objects.filter(url=url).first()
        vid.checked = True
        vid.check_status = CheckStatus.ACCOUNT_TERMINATED.value
        vid.save()
        return vid
