from django.core.management.base import BaseCommand, CommandError
from processor.models import Videos, Channels, CheckStatus, Categories
from processor.encoding_helpers import reconstruct_utf8_list_from_str_utf8_bstr_saved_as_latin1_swedish, reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish
from django.db.models.functions import Length
from django.db import transaction


class Command(BaseCommand):
    help = 'strip python byte string encoding in db videos'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        with transaction.atomic():
            chan: Channels
            for chan in Channels.objects.all():
                print(chan.id)
                chan.name = reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(chan.name)
                chan.description = reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(chan.description)
                chan.save()
        vid: Videos
        youtube_vids = Videos.objects.annotate(url_len=Length("url")).filter(url_len=11)
        for vid in youtube_vids:
            print(f"enter id: {vid.id}")
            utf8mb4_title = reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(vid.title)
            utf8m4_description = reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(vid.description)
            utf8m4_keywords = reconstruct_utf8_list_from_str_utf8_bstr_saved_as_latin1_swedish(vid.keywords)
            print(f"{vid.id=}, url={vid.url}, {utf8mb4_title=}, {utf8m4_description=}, {utf8m4_keywords=}")
            vid.title = utf8mb4_title
            vid.description = utf8m4_description
            vid.keywords = utf8m4_keywords
            vid.save()
        self.stdout.write(self.style.SUCCESS("Successfully transformed b-strings videos"))
