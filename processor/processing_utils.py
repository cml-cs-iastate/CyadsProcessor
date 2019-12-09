from __future__ import annotations
import pathlib
from dataclasses import dataclass
from pathlib import Path

from processor.models import Batch, Locations

import logging
logger = logging.getLogger(__name__)


@dataclass
class DumpPath:
    # Root path of data dir
    base_path: Path
    location: str
    host_hostname: str
    container_hostname: str
    time_started: int

    @staticmethod
    def from_ad_dir(ad_dir: Path) -> DumpPath:
        """ad_dir: Directory where ad files are stored for specific batch"""
        parents = ad_dir.parents
        start_timestamp = int(ad_dir.name)
        logger.info(f"servercontainer: {parents[0].name}")
        server_hostname, container_hostname = parents[0].name.split("#")
        location = parents[1].name
        base_path = parents[2]

        return DumpPath(base_path=base_path,
                        location=location,
                        host_hostname=server_hostname,
                        container_hostname=container_hostname,
                        time_started=start_timestamp,
                        )

    @staticmethod
    def from_batch(base_path: Path, batch: Batch) -> DumpPath:
        #location: Locations = Locations.objects.get(batch.location)
        return DumpPath(base_path=base_path,
                        location=batch.location.state_name,
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
                          attempt=int(attempt),
                          request_timestamp=int(request_timestamp),
                          video_watched=video_watched,
                          ext=ext,
                          file_path=file_path)


class AdFile:
    def __init__(self, filename: pathlib.Path):
        (self.bot_name,
         self.try_num,
         self.ad_seen_at,
         self.video_watched) = filename.stem.split("#")


class DumpFile:
    def __init__(self, filename: pathlib.Path):
        (self.bot_name,
         self.try_num,
         self.ad_seen_at,
         self.video_watched) = filename.stem.split("#")