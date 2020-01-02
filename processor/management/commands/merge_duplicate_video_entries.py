from django.core.management.base import BaseCommand, CommandError
from processor.models import Videos, Channels, CheckStatus, Ad_Found_WatchLog, Categories
from django.db.models import Count


class Command(BaseCommand):
    help = 'Merge duplicate video entries into one'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        dup_urls = Videos.objects.values("url").annotate(url_copies=Count("url")).filter(url_copies__gte=2).order_by('-url_copies')
        missing_channel_id: int = Channels.objects.only("id").get(name="missing").id
        missing_category_id: int = Categories.objects.only("id").get(name="missing").id
        print(f"all dups: {dup_urls}")
        for dup_url in dup_urls:
            filter_url = dup_url["url"]
            print(f"FRemoving duplicates of video: {dup_url}")
            # 1. get video rows of all of the url instance
            dups = Videos.objects.filter(url=filter_url)
            assert len(dups) >= 1
            # 2. Use the 1st video instance to hold all gathered info
            # Use the first video as the defaults
            dest_id: Videos = dups.first()
            # Don't count destination video as a duplicate
            dup_vid_ids_except_new = set(dup.id for dup in dups)
            dup_vid_ids_except_new.remove(dest_id.id)

            title = dups.first().title
            category = dups.first().category
            channel = dups.first().channel
            description = dups.first().description
            keywords = dups.first().keywords

            # Sum all counts
            watched_as_ad = 0
            watched_as_video = 0
            adfile_id = None
            checked: bool = False
            check_status = CheckStatus.NOT_CHECKED.value

            vid: Videos
            for vid in dups:
                print("ENTERED", repr(vid), "adfile=", adfile_id)
                if vid.AdFile_ID is not None:
                    # No duplicate adfile entries for same video
                    try:
                        assert adfile_id is None
                    except AssertionError:
                        raise AssertionError(f"Video: {vid!r} and dest_vid={dest_id.id}, {dest_id.AdFile_ID}, {dest_id.AdFile_ID.__dict__}, {dest_id.url} both have an AdFile entry")
                    dest_id = vid
                    adfile_id = vid.AdFile_ID
                    checked = True
                    assert vid.check_status == "FOUND"
                    check_status = vid.check_status
                if vid.title != "":
                    title = vid.title
                if vid.description != "":
                    description = vid.description
                if vid.keywords != "" or vid.keywords != "[]":
                    keywords = vid.keywords
                watched_as_ad += vid.watched_as_ad
                watched_as_video += vid.watched_as_video
                if vid.channel.id != missing_channel_id:
                    channel = vid.channel
                new_info = vid.category.id != missing_category_id
                if new_info:
                    category = vid.category

            destination_video: Videos = Videos.objects.get(pk=dest_id.id)
            destination_video.category = category
            destination_video.channel = channel
            destination_video.checked = checked
            destination_video.check_status = check_status
            destination_video.description = description
            destination_video.AdFile_ID = adfile_id
            destination_video.watched_as_video = watched_as_video
            destination_video.watched_as_ad = watched_as_ad
            destination_video.keywords = keywords
            destination_video.title = title
            print(f"updated video: Video: id={destination_video.id}, url={destination_video.url}")
            destination_video.save()
            # Replace the duplicate video ids in watchlog with single copy
            Ad_Found_WatchLog.objects.filter(ad_video__in=dup_vid_ids_except_new).update(ad_video=dest_id)
            Ad_Found_WatchLog.objects.filter(video_watched__in=dup_vid_ids_except_new).update(video_watched=dest_id)


            # Delete all but single video copy
            res = Videos.objects.filter(id__in=dup_vid_ids_except_new).delete()
            print(f"{res=}")

            # 2a. In the case that one has an adfile fk move all the info from others to it.
            # 2b. If it none have an adfile fk, then choose the first which has the most info

            # 3. Get all the ad watchlogs which
        self.stdout.write(self.style.SUCCESS("Successfully printed a video url"))
