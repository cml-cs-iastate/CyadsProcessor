from __future__ import annotations
from typing import Iterator
import io
import re
import bot_api
import json

import pathlib
from more_itertools import ilen
from bot_api import (BatchCompleted, BatchCompletionStatus)
from datetime import datetime
from processor.processing_utils import DumpPath, DumpFile
from processor.models import Batch


def count_txt_files(ad_dir: pathlib.Path) -> int:
    """Ad format v3"""
    return ilen(ad_dir.glob("Bot*.txt"))


def count_xml_files(ad_dir: pathlib.Path) -> int:
    return ilen(xml_files(ad_dir))


def xml_files(ad_dir: pathlib.Path) -> Iterator[pathlib.Path]:
    return ad_dir.glob("*.xml")


def html_files(ad_dir: pathlib.Path) -> Iterator[pathlib.Path]:
    return ad_dir.glob("*.html")


def extract_ip_from_html_player(html_filehandle: io.TextIOWrapper):
    """Returns 0.0.0.0 if no ip address is found in the html file"""
    html_file = html_filehandle.read()
    ip_containing = re.search(r"(?:\\u0026v|%26|%3F)ip(?:%3D|=)(.*?)(?:,|;|%26|\\u0026)", html_file, re.DOTALL)
    if ip_containing is None:
        return "0.0.0.0"
    return ip_containing.group(1)


def count_non_ad_requests(ad_dir: pathlib.Path) -> int:
    try:
        return ilen(ad_dir.joinpath("noAds.csv").open())
    except FileNotFoundError:
        return 0


def last_request_time(ad_dir: pathlib.Path) -> int:
    """Returns -1 for a request time if there were no requests with no ads"""
    try:
        ad_filenames = ad_dir.joinpath("noAds.csv").open().read().splitlines()[-10:]
        for ad_filename in reversed(ad_filenames):
            try:
                abs_ad_filepath: pathlib.Path = ad_dir / ad_filename
                return int(DumpFile(abs_ad_filepath).ad_seen_at)
            except (AttributeError, ValueError):
                # Possible file corruption
                print("FILE CORRUPTION IN FOLLOWING DIRECTORY")
                print(abs_ad_filepath)
                continue
        else:
            return -1
    except FileNotFoundError:
        version = determine_ad_format_version(ad_dir)
        if version == 3:
            ads = list(ad_dir.glob("*.txt"))
        elif version == 2:
            ads = list(ad_dir.glob("*.json"))
        elif version == 1:
            ads = list(ad_dir.glob("*.xml"))
        else:
            raise NotImplemented(f"ad format `{version}` not implemented for finding last timestamp")

        if len(ads) == 0:
            return -1

        latest = -1
        for file in ads:
            if "run_type.txt" in file.as_posix():
                continue
            try:
                ad = DumpFile(file)
            except Exception as e:
                print("DDDD", e, file)
                raise e
            if int(ad.ad_seen_at) > latest:
                latest = int(ad.ad_seen_at)
        return latest


def batch_is_old(dump_file: DumpPath):
    age_of_batch = datetime.now() - datetime.utcfromtimestamp(dump_file.time_started)
    age_hours_threshold = 24
    batch_age_hours = age_of_batch.days * 24 + age_of_batch.seconds / 60 / 60
    return batch_age_hours >= age_hours_threshold


def count_json_files(ad_dir: pathlib.Path) -> int:
    return ilen(ad_dir.glob("*.json"))


def determine_ad_format_version(ad_dir: pathlib.Path) -> int:
    """ad_dir: The parent directory where the ad files are stored (xml, json)"""

    # Is it version 2+?
    try:
        with ad_dir.joinpath("ad_format_version").open("r") as f:
            version = int(f.read())
            return version
    except FileNotFoundError:
        # If not assume version 1
        return 1


def reconstruct_completion_msg(dump_dir: DumpPath) -> BatchCompleted:
    """ad_dir: parent directory directly containing xml/json ad files
    returns a `BatchCompleted` message object"""

    # Hack for no metadata about number of bots ran
    try:
        batch = Batch.objects.get(location__state_name=dump_dir.location,
                                  start_timestamp=dump_dir.time_started,
                                  server_hostname=dump_dir.host_hostname,
                                  server_container=dump_dir.container_hostname,
                                  )
        num_bots = batch.total_bots
        external_ip = batch.external_ip
    except Batch.DoesNotExist as e:
        logfile = next(dump_dir.to_path().glob("bots_*.log"))
        external_ip = "0.0.0.0"

        with logfile.open() as f:
            for line in f:
                jline = json.loads(line)
                try:
                    num_bots = int(jline["num_bots"])
                    print("batch:", dump_dir, "has", num_bots, "bot(s)")
                    break
                except KeyError:
                    continue

    version: int = determine_ad_format_version(dump_dir.to_path())

    # Version 3 of ad format we collect ad urls in .txt
    if version == 3:
        ad_count = count_txt_files(dump_dir.to_path())
    # Version 2 of ad format Google stores ad info in .json
    elif version == 2:
        ad_count = count_json_files(dump_dir.to_path())
    # Version 1 of ad format Google stored ad info in .xml vast responses
    elif version == 1:
        ad_count = count_xml_files(dump_dir.to_path())
    else:
        raise NotImplemented(f"version: `{version}` not handled")

    non_ads = count_non_ad_requests(dump_dir.to_path())
    total_requests = ad_count + non_ads
    last_request = last_request_time(dump_dir.to_path())

    # Count size of the video list bots watched
    with open("political_videos.csv") as f:
        video_list_size = sum(1 for _ in f)
    completion_msg = BatchCompleted(status=BatchCompletionStatus.COMPLETE, hostname=dump_dir.container_hostname,
                                    run_id=dump_dir.time_started,
                                    external_ip=external_ip, bots_in_batch=num_bots,
                                    requests=total_requests, host_hostname=dump_dir.host_hostname,
                                    location=dump_dir.location, ads_found=ad_count, timestamp=last_request,
                                    video_list_size=video_list_size,
                                    )
    return completion_msg


# def ad_dir_from_parts(base_dir: Path, location: str, host_hostname: str, container_hostname: str,
#                      start_time: str) -> DumpDir:
#    ad_dir = base_dir.joinpath(location).joinpath(f"{host_hostname}#{container_hostname}").joinpath(start_time)
#    return DumpDir(ad_dir=ad_dir)
