from bs4 import BeautifulSoup
import urllib.parse

from youtube_dl.extractor.youtube import YoutubeIE, ExtractorError

from typing import TextIO, Union
from io import TextIOWrapper


class Parser:


    def __init__(self, xml: Union[str, TextIOWrapper]):
        """Parses a vast 3.0 xml file
        :param xml: vast xml to parse

        :raises ValueError: When no video ad urls (MediaFile) are present
        """
        try:
            with open(xml, "r", encoding="utf-8") as vast_handle:
                self.soup = BeautifulSoup(vast_handle, "xml")
        except TypeError:
            self.soup = BeautifulSoup(xml, "xml")

        if not self._supported_ad_types():
            raise ValueError("No video ad info inside")

    def _supported_ad_types(self):
        """Checks whether a vast file contains a video ad"""
        video_ads_types = self.soup.find(
            "MediaFile", attrs={
                "type": ["video/mp4",
                         "video/webm",
                         "video/3gpp,"
                         ]
            })
        if video_ads_types is None:
            return False
        return True

    @property
    def ad_system(self):
        """Returns the ad system used to deliver the ad"""
        advertiser = self.soup.find("AdSystem")
        if advertiser:
            return advertiser.text
        return ""

    @property
    def video_id(self):
        """Returns the youtube id of an ad hosted on Youtube"""
        media_files = self.soup.findAll("MediaFile")
        media_file_with_highest_bitrate = self._max_bit_rate(media_files)
        ad_url = media_files[media_file_with_highest_bitrate].text
        youtube_ad_url = self._extract_youtube_video_id(ad_url)
        if youtube_ad_url is not None:
            return youtube_ad_url
        return ad_url

    @classmethod
    def _extract_youtube_video_id(cls, youtube_url: str) -> str:
        "Extract the video id out of a youtube url"
        if "www.youtube.com" not in youtube_url:
            return youtube_url
        try:
            video_id = YoutubeIE.extract_id(youtube_url)
            return video_id
        except ExtractorError:
            video_id = cls.extract_video_from_api(youtube_url)
            return video_id

    @classmethod
    def extract_video_from_api(cls, youtube_url: str) -> str:
        url_parts = urllib.parse.urlparse(youtube_url)
        query = url_parts.query
        parsed_query = urllib.parse.parse_qs(query)
        if "video_id" in parsed_query:
            video_id = parsed_query["video_id"][0]
            return video_id
        return youtube_url

    @classmethod
    def _max_bit_rate(cls, media_files):
        max_pixels = 0
        position = 0
        for pos, media in enumerate(media_files):
            width = int(media.get("width"))
            height = int(media.get("height"))
            pixels = width * height
            if pixels < max_pixels:
                continue
            max_pixels = pixels
            position = pos
        return position

    @property
    def duration(self) -> int:
        """Returns the duration of the ad in seconds"""
        duration: str = self.soup.find("Duration").text
        length_of_ad = self._military_time_to_seconds(duration)
        return length_of_ad

    @property
    def skip_offset(self) -> int:
        linear = self.soup.findAll("Linear")
        for subsection in linear:
            if subsection.attrs:
                offset: str = subsection.get("skipoffset")
                offset_duration = self._military_time_to_seconds(offset)
                return offset_duration
        return 0

    @staticmethod
    def _military_time_to_seconds(time: str) -> int:
        SECONDS_IN_AN_HOUR = 3600
        SECONDS_IN_A_MINUTE = 60
        hours, minutes, seconds = time.split(":")
        return (int(hours) * SECONDS_IN_AN_HOUR
                + int(minutes) * SECONDS_IN_A_MINUTE
                + int(seconds)
                )