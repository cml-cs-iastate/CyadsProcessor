from pathlib import Path

from django.test import TestCase
from processor.models import Videos, CheckStatus, AdFile
from downloader.tasks import record_download_video, DuplicateVideoError
import tempfile


class Download(TestCase):
    missing_vid = "MISSING_VID"
    present_vid = "kPBtDHiHJuM"
    double_vid = "ZwibqZ044Ac"
    private_vid = "C5MgLA_qQhY"
    user_removed_vid = "XQh5Kl2kYz0"
    terminated_account_vid = "VxgMmqgaZsk"

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        # Workaround for needing a category id when just testing video downloading
        missing = Videos.objects.missing(vid_url=self.missing_vid)
        missing.save()
        external = Videos.objects.external(vid_url=self.present_vid)
        external.save()

        double = Videos.objects.external(vid_url=self.double_vid)
        double.save()

        private = Videos.objects.missing(vid_url=self.private_vid)
        private.save()

        _v = Videos.objects.missing(vid_url=self.user_removed_vid)
        _v.save()

        _v = Videos.objects.missing(vid_url=self.terminated_account_vid)
        _v.save()


    def tearDown(self):
        self.temp_dir.cleanup()

    def test_private_vid_marked_as_private(self):
        record_download_video(self.private_vid, self.temp_dir.name)
        vid: Videos = Videos.objects.get(url=self.private_vid)
        self.assertEqual(CheckStatus[vid.check_status], CheckStatus.PRIVATE)
        self.assertEqual(vid.checked, True)
        vid.save()
        print(vid)

    def test_video_removed_by_user_marked(self):
        record_download_video(self.user_removed_vid, self.temp_dir.name)
        vid = Videos.objects.get(url=self.user_removed_vid)
        self.assertEqual(CheckStatus[vid.check_status], CheckStatus.USER_REMOVED)

    def test_video_terminated_account_marked(self):
        vid = record_download_video(self.terminated_account_vid, self.temp_dir.name)
        vid.save()
        vid = Videos.objects.get(url=self.terminated_account_vid)
        self.assertEqual(CheckStatus[vid.check_status], CheckStatus.ACCOUNT_TERMINATED)

    def test_duplicate_videos_raises_errors(self):
        record_download_video(self.double_vid, self.temp_dir.name)
        with self.assertRaises(DuplicateVideoError):
            record_download_video(self.double_vid, self.temp_dir.name)

    def test_missing_vid_gets_marked_as_missing_downloaded(self):
        record_download_video(self.missing_vid, self.temp_dir.name)
        missing_video: Videos = Videos.objects.get(url=self.missing_vid)
        self.assertEqual(CheckStatus[missing_video.check_status], CheckStatus.MISSING)
        self.assertEqual(missing_video.checked, True)
        missing_video.save()

    def test_present_vid_is_downloaded(self):
        record_download_video(self.present_vid, self.temp_dir.name)
        present_vid: Videos = Videos.objects.get(url=self.present_vid)
        self.assertEqual(present_vid.AdFile_ID.ad_filepath, f"CyAds/kPBtDHiHJuM.mkv")
        self.assertTrue(Path(self.temp_dir.name).joinpath(present_vid.AdFile_ID.ad_filepath).exists())

        self.assertEqual(CheckStatus[present_vid.check_status], CheckStatus.FOUND)
        self.assertEqual(present_vid.checked, True)
