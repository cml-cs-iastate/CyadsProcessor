from django.core.management.base import BaseCommand, CommandError
from processor.models import Videos, Channels, CheckStatus
import re

class Command(BaseCommand):
    help = 'strip python byte string encoding in db videos'

    def add_arguments(self, parser):
        pass
        #parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        binary_str_regex = re.compile(r"""b['"].*['"]""")
        vid: Videos
        count = 0
        matches = 0
        for vid in Videos.objects.all():
            got_match = False
            if binary_str_regex.match(vid.title):
                vid.title = vid.title[2:-1]
                got_match = True
            if binary_str_regex.match(vid.description):
                vid.description = vid.description[2:-1]
                got_match = True
            if binary_str_regex.match(vid.keywords):
                vid.keywords = vid.keywords[2:-1]
                got_match = True
            if got_match:
                vid.save()
                print(f"modified vidid: {vid.id}")
                matches += 1
            count += 1
            print(f"got through {count} videos. Made {matches} changes")

        matches = 0
        count = 0
        chan: Channels
        for chan in Channels.objects.all():
            match = False
            if binary_str_regex.match(chan.name):
                chan.name = chan.name[2:-1]
                match = True
            if match:
                print(f"modified channelid: {chan.id}")
                chan.save()
                matches += 1
            count += 1
            print(f"got through {count} channels. Made {matches} changes")
        self.stdout.write(self.style.SUCCESS("Successfully removed b-strings from channels and videos"))
