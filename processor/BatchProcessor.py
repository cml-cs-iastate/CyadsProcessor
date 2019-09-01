from __future__ import annotations
import glob
import logging

import os
from django.core.exceptions import ObjectDoesNotExist
from messaging.payloads.BatchPayload import BotEvents, BatchStarted, BatchCompleted, BatchSynced
from processor.models import Batch, Constants, Videos, Bots, Ad_Found_WatchLog, Categories, Channels
from processor.models import Locations, UsLocations
from processor.vast import Parser
from processor.video_metadata import VideoMetadata


import pathlib
from pathlib import Path

from dataclasses import dataclass


@dataclass
class DumpPath:
    # Root path of data dir
    base_path: Path
    location: str
    host_hostname: str
    container_hostname: str
    time_started: int

    @staticmethod
    def from_batch(base_path: Path, batch: Batch) -> DumpPath:
        return DumpPath(base_path=base_path,
                        location=batch.location,
                        host_hostname=batch.server_hostname,
                        container_hostname=batch.server_container,
                        time_started=batch.start_timestamp,
                        )

    def to_path(self) -> Path:
        """Converts the DumpPath into a traversable path on the filesystem"""
        return (
            self.base_path
                .joinpath(self.location)
                .joinpath(f"{self.host_hostname}#{self.container_hostname}")
                .joinpath(str(self.time_started))
        )

@dataclass
class FullAdPath:
    """Specific file of ad info"""
    dump_dir_info: DumpPath
    bot_name: str
    attempt: int
    request_timestamp: int
    video_watched: str
    ext: str
    file_path: Path

    @staticmethod
    def from_dump_path_and_file(dump_path: DumpPath, file_path: Path) -> FullAdPath:
        (bot_name,
        attempt,
        request_timestamp,
        video_watched) = file_path.stem.split("#")
        ext = file_path.suffix

        return FullAdPath(dump_dir_info=dump_path,
                          bot_name=bot_name,
                          attempt=attempt,
                          request_timestamp=request_timestamp,
                          ext=ext,
                          file_path=file_path)




class AdFile:
    def __init__(self, filename: pathlib.Path):
        (self.bot_name,
        self.try_num,
        self.ad_seen_at,
        self.video_watched) = filename.stem.split("#")


class BatchProcessor:

    logger = logging.getLogger(__name__)

    def __init__(self, event):
        self.event = event
        self.api_key = os.getenv('GOOGLE_KEY')
        self.dump_path = os.getenv('DUMP_PATH')

    def reset_database_connection(self):
        from django import db
        db.close_old_connections()

    def process(self, batch_data):

        # needs to be done because long idle connections might have been closed by mysql server
        self.reset_database_connection()

        if self.event == BotEvents.BATCH_STARTED.value:
            batch_data = BatchStarted.from_json(batch_data)
            self.process_batch_started(batch_data)

        elif self.event == BotEvents.BATCH_COMPLETED.value:
            batch_data = BatchCompleted.from_json(batch_data)
            self.process_batch_completed(batch_data)

        elif self.event == BotEvents.BATCH_SYNCED.value:
            batch_data = BatchSynced.from_json(batch_data)
            self.process_batch_synced(batch_data)

    def process_batch_started(self, batch_data):
        from processor.models import Batch
        self.logger.info("Saving batch started event")
        try:
            loc = self.get_location_info(batch_data.location)
            batch, created = Batch.objects.get_or_create(server_hostname=batch_data.host_hostname,
                                                         server_container=batch_data.hostname,
                                                         location=loc,
                                                         start_timestamp=batch_data.run_id)
            if created:
                batch.total_bots = batch_data.bots_started
                batch.external_ip = batch_data.external_ip
                batch.video_list_size = batch_data.video_list_size
                batch.save()
            else:
                self.logger.info("The batch information already exists")
        except Exception as e:
            self.logger.error("Error While saving batch started message into the database")
            self.logger.exception(str(e))
            raise e

    def process_batch_completed(self, batch_data):
        try:
            batch = Batch.objects.get(start_timestamp=batch_data.run_id,
                                      server_hostname=batch_data.host_hostname,
                                      server_container=batch_data.hostname,
                                      completed_timestamp=-1)
            batch.completed_timestamp=batch_data.timestamp
            batch.status = Constants.BATCH_COMPLETED
            batch.time_taken = batch.completed_timestamp - batch.start_timestamp
            batch.total_requests = batch_data.requests
            batch.total_ads_found = batch_data.ads_found
            batch.save()
        except ObjectDoesNotExist as err:
            self.logger.error("No such batch information found to mark as completed")
            print("No such batch information found to mark as completed")
            self.logger.error(str(batch_data))
            raise err

        except Exception as e:
            self.logger.error("Cannot save batch completed event into database")
            self.logger.exception(str(e))
            raise e

    def process_batch_synced(self, batch_data):
        batch_info = batch_data.batch_info
        try:
            loc = self.get_location_info(batch_info.location)
            batch, created = Batch.objects.get_or_create(start_timestamp=batch_info.run_id,
                                                         server_hostname=batch_info.host_hostname,
                                                         server_container=batch_info.hostname,
                                                         location=loc)
            batch.completed_timestamp = batch_info.timestamp
            batch.status = Constants.BATCH_COMPLETED
            batch.time_taken = batch.completed_timestamp - batch.start_timestamp
            batch.total_requests = batch_info.requests
            batch.total_ads_found = batch_info.ads_found
            batch.synced = True
            batch.external_ip = batch_info.external_ip
            batch.total_bots = batch_info.bots_started
            batch.video_list_size = batch_info.video_list_size
            batch.save()
            if created:
                self.process_new_batch(batch)
                batch.processed = True
                batch.save()
            else:
                self.logger.info("Batch is already processed. -- deleting all the data and reprocessing again")
                batch.delete()
                self.process_batch_synced(batch_data)
        except Exception as e:
            self.logger.error("Error While saving batch synced message into the database")
            self.logger.exception(str(e))
            raise e

    def get_location_info(self,location):
        loc, created = Locations.objects.get_or_create(state_name=location,
                                                       state_symbol=UsLocations().get_state_abb(location))
        return loc

    def process_new_batch(self, batch: Batch):
        dump_path: DumpPath = DumpPath.from_batch(base_path=self.dump_path, batch=batch)
        if not dump_path.to_path().is_dir():
            self.logger.info('No such dump path found ')
            raise RuntimeError('No such dump path found for processing ' + dump_path)
        self.save_video_information(dump_path)
        self.save_ad_information(dump_path)
        self.save_watchlog_information(dump_path, batch)

    def determine_ad_format_version(self, dump_path: DumpPath) -> int:

        # Is it version 2+?
        try:
            with dump_path.to_path().joinpath("ad_format_version").open("r") as f:
                version = int(f.read())
                return version
        except FileNotFoundError:
            # version 1 had no `ad_format_version` to indicate versioning
            return 1


    def save_watchlog_information(self, dump_path: DumpPath, batch: Batch):
        ad_format_version: int = self.determine_ad_format_version(dump_path)
        if ad_format_version == 1:
            videos = glob.glob(dump_path.to_path().joinpath('Bot*.xml'))
            for video in videos:
                try:
                    parsed_ad = Parser(video)
                    video_ad = Videos.objects.filter(url=parsed_ad.video_id)
                    video_ad = video_ad[0]
                    if len(parsed_ad.video_id) == 11:
                        source = 'youtube'
                    else:
                        source = 'external'

                    parsed_file = self.parse_video_pattern(video.replace(dump_path, ''))
                    vid = Videos.objects.filter(url=parsed_file['video_id'])
                    vid = vid[0]
                    bot = self.save_bots(parsed_file['bot_name'])
                    attempt = parsed_file['try']
                    request_timestamp = parsed_file['request_timestamp']
                    wl, created = Ad_Found_WatchLog.objects.get_or_create(batch=batch, video_watched=vid, attempt=attempt,
                                                                          request_timestamp=request_timestamp, bot=bot,
                                                                          ad_video=video_ad)
                    wl.ad_source = source
                    wl.ad_duration = parsed_ad.duration
                    wl.ad_skip_duration = parsed_ad.skip_offset
                    wl.ad_system = parsed_ad.ad_system
                    wl.save()
                except Exception as e:
                    self.logger.info("Cannot parse the vast file. No Ad information was found")
        elif ad_format_version == 2:
            self.logger.error("Version 2 parsing not impleented for ad format parsing")
        elif ad_format_version == 3:
            videos = dump_path.to_path().glob("Bot*.txt")
            for video in videos:
                view_path: FullAdPath = FullAdPath.from_dump_path_and_file(dump_path, video)
                ad_caught: str = view_path.file_path.open("r").read()

            wl = Ad_Found_WatchLog()
        else:
            self.logger.error(f"Future/unexpected ad format version not implemented: {ad_format_version}")

    def save_ad_information(self, dump_path):
        videos = glob.glob(dump_path + '/Bot*.xml')
        ad_list = []
        for video in videos:
            #parse the vast xml
            try:
                parsed_ad = Parser(video)
                if len(parsed_ad.video_id) == 11:
                    ad_list.append(parsed_ad.video_id)
                else:
                    cat = self.save_categories(0, 'external')
                    channel = self.save_channel('0', 'external')
                    vid, created = Videos.objects.get_or_create(url=parsed_ad.video_id,
                                                                category=cat, channel=channel)
                    vid.keywords = ''
                    vid.description = ''
                    vid.title = ''
                    vid.watched_as_ad = vid.watched_as_ad + 1
                    vid.save()
            except Exception as e:
                self.logger.info("Cannot parse the vast file. No Ad information was found")

            if len(ad_list) == 50:
                self.save_video_metadata(ad_list, True)
                ad_list.clear()
        self.save_video_metadata(ad_list)

    def save_video_information(self, dump_path):

        videos = glob.glob(dump_path + '/Bot*.xml')
        video_list = []
        for video in videos:
            if len(video_list) == 50:
                self.save_video_metadata(video_list)
                video_list.clear()
            video = video.replace(dump_path, '')
            parsed_file = self.parse_video_pattern(video)
            video_list.append(parsed_file['video_id'])
        self.save_video_metadata(video_list)

    def save_video_metadata(self,video_list, is_ad=False):
        all_metadata = VideoMetadata(video_list, self.api_key)
        for i in range(len(all_metadata)):
            print(i)
            print(all_metadata.category_name)
            print(all_metadata.id)
            metadata = all_metadata.__next__()
            cat = self.save_categories(metadata.category_id,metadata.category_name)
            channel = self.save_channel(metadata.channel_id, metadata.channel_title)
            vid, created = Videos.objects.get_or_create(url=metadata.id,
                                                        category=cat, channel=channel)
            vid.keywords = str(metadata.keywords).encode('utf-8')
            vid.description = str(metadata.description).encode('utf-8')
            vid.title = str(metadata.title).encode('utf-8')
            if is_ad:
                vid.watched_as_ad = vid.watched_as_ad + 1
            else:
                vid.watched_as_video = vid.watched_as_video + 1
            vid.save()

    def save_channel(self, id, name):
        ch, created = Channels.objects.get_or_create(channel_id=id, name=str(name).encode('utf-8'))
        return ch

    def save_categories(self,cat_id, name):
        cat, created = Categories.objects.get_or_create(cat_id=cat_id, name=str(name).encode('utf-8'))
        return cat

    def save_bots(self,name):
        bot, created = Bots.objects.get_or_create(name=name)
        return bot

    def parse_video_pattern(self,video):

        pattern = video.split("#")
        bot_name = pattern[0].split("/")
        bot_name = bot_name[bot_name.__len__()-1]
        return {'bot_name': bot_name, 'try': pattern[1], 'request_timestamp': pattern[2],"video_id": pattern[3].split(".xml")[0]}










