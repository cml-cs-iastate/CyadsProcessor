from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from processor.models import Videos, Channels, CheckStatus
from django.db.models import Count
from dataclasses import dataclass

@dataclass
class TopChoice:


class Command(BaseCommand):
    help = 'Merge duplicate video entries into one'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        dup_urls = Videos.objects.values("url").annotate(url_copies=Count("url")).filter(url_copies__gte=2).order_by('-url_copies')
        print("length: ", len(dup_urls), dup_urls)

        for dup_url in dup_urls:

            # 1. get video rows of all of the url instance
            dups = Videos.objects.filter(dup_url)
            assert len(dups) >= 1
            # 2. decide on a particular url instance based on which has more info

            choice_made = False
            dest_id: Optional[int] = dups.first().id
            title = dups.first().title
            category = dups.first().category
            channel = dups.first().channel
            description = dups.first().description
            keywords = dups.first().keywords
            #Sum all counts?
            watched_as_ad = dups.first().watched_as_ad
            watched_as_video = dups.first().watched_as_ad
            adfile_id = None
            checked: bool = False
            check_status = CheckStatus.NOT_CHECKED.value

            vid: Videos
            for vid in dups:
                if vid.AdFile_ID is not None:
                    # No duplicate adfile entries for same video
                    assert adfile_id is not None
                    dest_id = vid.id
                    AdFile_ID = vid.AdFile_ID
                if vid.title != "":
                    title = vid.title
                if vid.description != "":
                    description = vid.description
                if vid.keywords != "" or vid.keywords != "[]":
                    keywords = vid.keywords
                watched_as_ad += vid.watched_as_ad
                watched_as_video +=  vid.watched_as_video







            # 2a. In the case that one has an adfile fk move all the info from others to it.
            # 2b. If it none have an adfile fk, then choose the first which has the most info

            # 3. Get all the ad watchlogs which
            break
        self.stdout.write(self.style.SUCCESS("Successfully printed a video url"))
