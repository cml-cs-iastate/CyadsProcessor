import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from downloader import tasks
from processor.models import AdFile
import sentry_sdk


def get_non_mp4_ad_entries():
    return AdFile.objects.exclude(ad_filepath__endswith="mp4")


def extract_yt_id(ad_filepath: str) -> str:
    return ad_filepath.split("/")[-1][:11]

class Command(BaseCommand):
    help = 'Redownload and replace non-mp4 ads with .mp4 versions'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        failures = 0
        non_mp4_entries = get_non_mp4_ad_entries()
        for non_mp4_entry in non_mp4_entries:
            try:
                sentry_sdk.set_context('django_management_command', {
                    'command': 'replace non-mp4 videos',
                    'existing_filepath': non_mp4_entry.ad_filepath,
                    'adfile_id': non_mp4_entry.id,
                })
                # 1. Download new video
                print("old adFile")
                print(non_mp4_entry)


                video_id = extract_yt_id(non_mp4_entry.ad_filepath)
                print(f"video_id: {video_id}")
                download_dir = os.environ["AD_ARCHIVE_FILESTORE_DIR"]
                replacement_file_path = tasks.video_download_with_collection(video_id, base_download_dir=download_dir, collection_type=non_mp4_entry.collection_type)
                print(f"replacement path: {replacement_file_path.as_posix()}")
                # 2. Verify it exists on LSS
                assert Path(download_dir).joinpath(replacement_file_path).exists()
                # 3. Update filepath in DB
                # store old filepath for later
                old_filepath = Path(download_dir).joinpath(non_mp4_entry.ad_filepath)
                non_mp4_entry.ad_filepath = replacement_file_path.as_posix()
                print("updated ad_filepath obj")
                print(non_mp4_entry)
                non_mp4_entry.save()
                # 4. Delete video at old filepath from LSS
                old_filepath.unlink(missing_ok=True)
                print("deleted old filepath", old_filepath.as_posix())
            except Exception as err:
                failures += 1
                sentry_sdk.capture_exception(err)
                continue
        if failures > 0:
            self.stderr.write(self.style.FAILED(f"({failures}) videos failed to be replaced with mp4 versions"))
        else:
            self.stdout.write(self.style.SUCCESS("Successfully replaced non-mp4 files"))
