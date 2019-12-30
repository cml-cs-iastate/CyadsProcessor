from pathlib import Path

from django.test import TestCase

import processor.encoding_helpers
from processor.models import Videos, CheckStatus, AdFile, Channels, Categories
import tempfile

from django.db import IntegrityError
from processor.encoding_helpers import convert_non_ascii_list_to_encodeable_ascii, \
    convert_non_ascii_string_to_encodeable_ascii
import processor.processing_utils


class Integrity(TestCase):
    missing_vid = "MISSING_VID"
    present_vid = "kPBtDHiHJuM"
    double_vid = "ZwibqZ044Ac"
    private_vid = "C5MgLA_qQhY"

    def setUp(self):
        # Workaround for needing a category id when just testing video downloading
        pass

    def test_duplicate_urls_violate_rules(self):
        channel = Channels.objects.missing()
        category = Categories.objects.missing()
        vid_first = Videos.objects.create(url=self.present_vid, channel=channel, category=category)
        vid_first.save()
        with self.assertRaises(IntegrityError):
            vid_second = Videos.objects.create(url=self.present_vid, channel=channel, category=category)
            vid_second.save()

    def test_lists_save_no_byte_strings(self):
        channel = Channels.objects.missing()
        category = Categories.objects.missing()

        sample_list = ["😜", "😜", "😜"]
        sample_title = "😲😜🤑🙈 | HOW TO PUT EMOJI'S ON YOUR YOUTUBE TITLES"
        vid: Videos = Videos.objects.create(url=self.present_vid, channel=channel, category=category)
        vid.title = convert_non_ascii_string_to_encodeable_ascii(sample_title)
        vid.keywords = convert_non_ascii_list_to_encodeable_ascii(sample_list)
        vid.description = convert_non_ascii_string_to_encodeable_ascii("hello")
        vid.save()
        vid_get = Videos.objects.get(url=self.present_vid)
        self.assertEqual(vid.title, "\\xf0\\x9f\\x98\\xb2\\xf0\\x9f\\x98\\x9c\\xf0\\x9f\\xa4\\x91\\xf0\\x9f\\x99\\x88 | HOW TO PUT EMOJI'S ON YOUR YOUTUBE TITLES")

        # Verify we can recover the result
        title_reconverted = processor.encoding_helpers.reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(vid.title)
        keywords_reconverted = processor.encoding_helpers.reconstruct_utf8_list_from_str_utf8_bstr_saved_as_latin1_swedish(vid.keywords)

        self.assertEqual(title_reconverted, sample_title)
        self.assertEqual(keywords_reconverted, sample_list)
