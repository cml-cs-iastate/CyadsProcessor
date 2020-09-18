from __future__ import annotations

from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from enum import Enum

from messaging.payloads.BatchPayload import BatchCompletionStatus, BatchSyncComplete, BatchSynced, BatchCompleted
from processor.encoding_helpers import convert_non_ascii_string_to_encodeable_ascii

# Magic constants for db models
# Using throughout models which don't allow null to indicate missing
MISSING_ID = -1
MISSING_NAME = "missing"

# Using throughout models which don't allow null to indicate external
EXTERNAL_ID = 0
EXTERNAL_NAME = "external"


class Constants:
    BATCH_STARTED = 'Started'
    BATCH_COMPLETED = 'Completed'
    BATCH_RUNNING = 'Running'


class UsLocations:
    states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
    }

    def get_state_abb(self, state):
        res = [k for k, v in self.states.items() if v.lower() == state.lower()]
        if res.__len__() == 1:
            return res[0]
        else:
            return state


class Locations(models.Model):
    state_name = models.CharField(max_length=100)
    state_symbol = models.CharField(max_length=100)


class Batch(models.Model):
    """Stores info about a batch of bots. Used by :model:`processor.Ad_Found_WatchLog`"""
    start_timestamp = models.BigIntegerField(help_text="DateTime the batch of bots was started")
    completed_timestamp = models.BigIntegerField(default=-1, help_text="DateTime the batch of bots finished running")
    time_taken = models.IntegerField(default=-1, help_text="Time taken for batch to run through video list repetitions")
    location = models.ForeignKey(Locations, on_delete=models.PROTECT)
    total_bots = models.IntegerField(default=0, help_text="Number of bots ran that were part of the batch")
    server_hostname = models.CharField(max_length=30, default='NOT_FOUND_IN_JSON', help_text="The hostname of the server the bots ran on")
    server_container = models.CharField(max_length=30, default='NOT_FOUND_IN_JSON', help_text="The docker container hostname (or same as server_hostname if not ran under docker)")
    external_ip = models.CharField(max_length=30, default='0.0.0.0', help_text="The IP address that YouTube would sees")
    status = models.CharField(max_length=20, default=Constants.BATCH_RUNNING, help_text="Status of batch, See Constants")
    synced = models.BooleanField(default=False, help_text="Is the batch data synced to the server yet?")
    processed = models.BooleanField(default=False, help_text="Has the synced batch data been processed yet?")
    total_requests = models.IntegerField(default=0, help_text="Number of video requests the entire batch of bots made to YouTube")
    total_ads_found = models.IntegerField(default=0, help_text="Number of ads shown to the whole batch of bots")
    video_list_size = models.IntegerField(default=550, help_text="Number of videos in the video list the bots watched")
    remarks = models.CharField(max_length=255, help_text="Used to indicated any problems with the batch data")

    class Meta:
        ordering = ['-start_timestamp']

    @staticmethod
    def get_batch_by_status(status):
        batch = Batch.objects.get(status=status)
        return batch.objects.all()

    def into_batch_synced(self) -> BatchSynced:
        # Safety: Batch must be marked as synced to convert to synced
        assert self.synced
        completion_msg: BatchCompleted = BatchCompleted(ads_found=self.total_ads_found,
                                                        bots_started=self.total_bots,
                                                        external_ip=self.external_ip,
                                                        host_hostname=self.server_hostname,
                                                        hostname=self.server_container,
                                                        location=self.location.state_name,
                                                        requests=self.total_requests,
                                                        run_id=self.start_timestamp,
                                                        timestamp=self.completed_timestamp,
                                                        status=BatchCompletionStatus.COMPLETE,
                                                        video_list_size=self.video_list_size,
                                                        )
        # Anything that is marked as synced, is assumed synced without errors
        batch_synced: BatchSynced = BatchSynced(batch_info=completion_msg, sync_result=BatchSyncComplete())
        return batch_synced


class Bots(models.Model):
    """A particular bot in a Batch"""
    name = models.CharField(max_length=100, help_text="Name given to bots, Keeps bot data from mixing together")

    def __str__(self) -> str:
        return self.name


class CategoryManager(models.Manager):

    def from_valid_category_and_name(self, category_id: int, name: str) -> Categories:
        encoded_name = convert_non_ascii_string_to_encodeable_ascii(name)
        try:

            cat, created = self.get_or_create(cat_id=category_id, name=encoded_name)
            return cat
        except MultipleObjectsReturned:
            # Return first
            return self.filter(cat_id=category_id, name=encoded_name).first()

    def missing(self) -> Categories:
        cat, created = self.get_or_create(cat_id=MISSING_ID, name=MISSING_NAME)
        return cat

    def external(self) -> Categories:
        cat, created = self.get_or_create(cat_id=EXTERNAL_ID, name=EXTERNAL_NAME)
        return cat


class Categories(models.Model):
    """The YouTube category of a :model:`processor.Videos`"""

    cat_id = models.IntegerField(help_text="Numeric category id used by YouTube Data API for each video categories")
    name = models.CharField(max_length=100, help_text="Name of video category")

    objects = CategoryManager()

    def __repr__(self):
        return f"<Categories({self.id}): cat_id={self.cat_id}, name={self.name}>"

    def mark_missing(self):
        self.cat_id = MISSING_ID
        self.name = MISSING_NAME

    def mark_external(self):
        self.cat_id = EXTERNAL_ID
        self.name = EXTERNAL_NAME

    def is_missing(self) -> bool:
        """The video is missing and thus the category cannot be found"""
        return self.cat_id == MISSING_ID and self.name == MISSING_NAME

    def is_external(self) -> bool:
        """The video is externally hosted from YouTube and thus has no YouTube category"""
        return self.cat_id == EXTERNAL_ID and self.name == EXTERNAL_NAME


class ChannelManager(models.Manager):

    def from_valid_channel_and_name(self, channel_id: int, name: str) -> Channels:
        encoded_name = convert_non_ascii_string_to_encodeable_ascii(name)
        try:
            ch, created = self.get_or_create(channel_id=channel_id, name=encoded_name)
            return ch
        except MultipleObjectsReturned:
            # Use first
            return self.filter(channel_id=channel_id, name=encoded_name).first()

    def missing(self) -> Channels:
        chan, created = self.get_or_create(channel_id=MISSING_ID, name=MISSING_NAME)
        return chan

    def external(self) -> Channels:
        chan, created = self.get_or_create(channel_id=EXTERNAL_ID, name=EXTERNAL_NAME)
        return chan


class Channels(models.Model):
    """The YouTube channel associated with a YouTube :model:`processor.Videos`"""
    channel_id = models.TextField(help_text="Unique YouTube channel id")
    name = models.CharField(max_length=255, help_text="Name of the YouTube channel selected by channel owner")
    description = models.CharField(max_length=255, default='', help_text="Description of channel")
    objects = ChannelManager()

    def __repr__(self):
        return f"<Channels: id={self.id}, channel_id={self.channel_id}, name={self.name}, description={self.description}>"

    def is_external(self) -> bool:
        return self.name == EXTERNAL_NAME and self.channel_id == EXTERNAL_ID

    def is_missing(self) -> bool:
        return self.name == MISSING_NAME and self.channel_id == MISSING_ID

    def mark_missing(self):
        self.cat_id = MISSING_ID
        self.name = MISSING_NAME

    def mark_external(self):
        self.cat_id = EXTERNAL_ID
        self.name = EXTERNAL_NAME


class CheckStatus(Enum):
    NOT_CHECKED = "NOT_CHECKED"
    FOUND = "FOUND"
    MISSING = "MISSING"
    ERROR = "ERROR"
    PRIVATE = "PRIVATE"
    USER_REMOVED = "USER_REMOVED"
    ACCOUNT_TERMINATED = "ACCOUNT_TERMINATED"
    LIVE_STREAM_REMOVED = "LIVE_STREAM_REMOVED"


class CollectionType(Enum):
    CYADS = "CyAds"
    GOOGLETREPORT = "GoogleTReport"


class AdFile(models.Model):
    """Stores data about where a downloaded video is located in storage"""
    id = models.AutoField(db_column="AdFile_ID", primary_key=True)
    ad_filepath = models.TextField(null=True, help_text="Relative filepath where downloaded video file is stored")
    collection_type = models.CharField(max_length=64, choices=[(tag, tag.value) for tag in CollectionType],
                                       help_text="Which :py:class:`Collection` the video file is part of")

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f' {self.id!r}, {self.ad_filepath!r},'
                f' {self.collection_type!r})')


class VideoManager(models.Manager):
    def external(self, vid_url: str) -> Videos:
        channel = Channels.objects.external()
        category = Categories.objects.external()
        vid, created = self.get_or_create(url=vid_url, channel=channel, category=category)
        return vid

    def missing(self, vid_url: str) -> Videos:
        channel = Channels.objects.missing()
        category = Categories.objects.missing()
        vid, created = self.get_or_create(url=vid_url, channel=channel, category=category)
        vid.check_status = CheckStatus.MISSING.value
        return vid


class Videos(models.Model):
    """Video metadata information"""
    url = models.TextField(help_text="URL to find video")
    title = models.TextField(default='', help_text="Title of YouTube video")
    category = models.ForeignKey(Categories, on_delete=models.PROTECT)
    channel = models.ForeignKey(Channels, on_delete=models.PROTECT)
    description = models.TextField(default='', help_text="The description provided for the YouTube video")
    keywords = models.TextField(default='', help_text="List of keywords/tags video publisher used for the video")
    watched_as_ad = models.IntegerField(default=0, help_text=">0 if video was viewed as an ad")
    watched_as_video = models.IntegerField(default=0, help_text=">0 if video was viewed due to a video request")
    AdFile_ID = models.ForeignKey(db_column="AdFile_ID", to=AdFile, on_delete=models.PROTECT, null=True)
    checked = models.BooleanField(null=False, default=False, help_text="Whether the video entry has been checked and downloaded")
    time_checked = models.DateTimeField(null=True, auto_now=True, help_text="Datetime the video was checked/downloaded")
    check_status = models.CharField(max_length=64, choices=[(tag, tag.value) for tag in CheckStatus],
                                    default=CheckStatus.NOT_CHECKED.value, help_text="What the result of the :py:class:`CheckStatus` is")

    objects = VideoManager()

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self.id!r}, {self.url!r}'
                f' {self.title!r}, {self.channel!r}'
                f' {self.category!r}'
                f' {self.description!r}, {self.keywords!r}'
                f' {self.watched_as_ad!r}, {self.watched_as_video!r}'
                f' {self.AdFile_ID!r}, {self.checked!r}'
                f' {self.time_checked!r}, {self.check_status!r}'
                f')'
                )


class Ad_Found_WatchLog(models.Model):
    """Info related to a particular :model:`Bots` request which yielded an ad :model:`Videos`"""
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, help_text="The batch the ad view is part of")
    bot = models.ForeignKey(Bots, on_delete=models.PROTECT, help_text="The bot the ad request was part of for a particular batch")
    video_watched = models.ForeignKey(Videos, on_delete=models.PROTECT, related_name='video_watched', help_text="The video request in the video list which had an ad view assoicated with it")
    attempt = models.IntegerField(default=0, help_text="Which repetition of viewing the same video request in the list")
    request_timestamp = models.BigIntegerField(default=0, help_text="The datetime the video was requested to view on YouTube")
    ad_video = models.ForeignKey(Videos, on_delete=models.PROTECT, related_name='ad_video', help_text="The ad shown")
    ad_source = models.CharField(max_length=50, default='youtube', help_text="YouTube hosted ad or externally hosted")
    ad_duration = models.IntegerField(default=0, help_text="How long the ad is in seconds")
    ad_skip_duration = models.IntegerField(default=0, help_text="Required time before ad can be skipped")
    ad_system = models.CharField(max_length=255, default='', help_text="Which ad serving provider the advertiser uses")

    def __repr__(self):
        return f"<AdFoundWatchLog({self.id}): batch={self.batch.id}, bot={self.bot.id}, video_watched={self.video_watched.id}, ad_video={self.ad_video.id}, {self.request_timestamp=}, {self.attempt=}"
