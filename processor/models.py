from __future__ import annotations

from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from enum import Enum

from messaging.payloads.BatchPayload import BatchCompletionStatus, BatchSyncComplete, BatchSynced, BatchCompleted

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
    start_timestamp = models.BigIntegerField()
    completed_timestamp = models.BigIntegerField(default=-1)
    time_taken = models.IntegerField(default=-1)
    location = models.ForeignKey(Locations, on_delete=models.PROTECT)
    total_bots = models.IntegerField(default=0)
    server_hostname = models.CharField(max_length=30, default='NOT_FOUND_IN_JSON')
    server_container = models.CharField(max_length=30, default='NOT_FOUND_IN_JSON')
    external_ip = models.CharField(max_length=30, default='0.0.0.0')
    status = models.CharField(max_length=20, default=Constants.BATCH_RUNNING)
    synced = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    total_requests = models.IntegerField(default=0)
    total_ads_found = models.IntegerField(default=0)
    video_list_size = models.IntegerField(default=550)
    remarks = models.CharField(max_length=255)

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
    name = models.CharField(max_length=100)


class CategoryManager(models.Manager):

    def from_valid_category_and_name(self, category_id: int, name: str) -> Categories:
        try:
            cat, created = self.get_or_create(cat_id=category_id, name=name.encode('utf-8'))
            return cat
        except MultipleObjectsReturned:
            # Return first
            return self.filter(cat_id=category_id, name=name.encode('utf-8')).first()

    def missing(self) -> Categories:
        cat, created = self.get_or_create(cat_id=MISSING_ID, name=MISSING_NAME)
        return cat

    def external(self) -> Categories:
        cat, created = self.get_or_create(cat_id=EXTERNAL_ID, name=EXTERNAL_NAME)
        return cat


class Categories(models.Model):
    cat_id = models.IntegerField()
    name = models.CharField(max_length=100)

    objects = CategoryManager()

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
        try:
            ch, created = self.get_or_create(channel_id=channel_id, name=name.encode('utf-8'))
            return ch
        except MultipleObjectsReturned:
            # Use first
            return self.filter(channel_id=channel_id, name=name.encode('utf-8')).first()

    def missing(self) -> Channels:
        chan, created = self.get_or_create(channel_id=MISSING_ID, name=MISSING_NAME)
        return chan

    def external(self) -> Channels:
        chan, created = self.get_or_create(channel_id=EXTERNAL_ID, name=EXTERNAL_NAME)
        return chan


class Channels(models.Model):
    channel_id = models.TextField()
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, default='')
    objects = ChannelManager()

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


class CollectionType(Enum):
    CYADS = "CyAds"
    GOOGLETREPORT = "GoogleTReport"


class AdFile(models.Model):
    id = models.AutoField(db_column="AdFile_ID", primary_key=True)
    ad_filepath = models.TextField(null=True)
    collection_type = models.CharField(max_length=64, choices=[(tag, tag.value) for tag in CollectionType])

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
    url = models.TextField()
    title = models.TextField(default='')
    category = models.ForeignKey(Categories, on_delete=models.PROTECT)
    channel = models.ForeignKey(Channels, on_delete=models.PROTECT)
    description = models.TextField(default='')
    keywords = models.TextField(default='')
    watched_as_ad = models.IntegerField(default=0)
    watched_as_video = models.IntegerField(default=0)
    AdFile_ID = models.ForeignKey(db_column="AdFile_ID", to=AdFile, on_delete=models.PROTECT, null=True)
    checked = models.BooleanField(null=False, default=False)
    time_checked = models.DateTimeField(null=True, auto_now=True)
    check_status = models.CharField(max_length=64, choices=[(tag, tag.value) for tag in CheckStatus],
                                    default=CheckStatus.NOT_CHECKED.value)

    objects = VideoManager()
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self.id!r}, {self.url!r}'
                f' {self.title!r}, {self.channel!r}'
                f' {self.description!r}, {self.keywords!r}'
                f' {self.watched_as_ad!r}, {self.watched_as_video!r}'
                f' {self.AdFile_ID!r}, {self.checked!r}'
                f' {self.time_checked!r}, {self.check_status!r}'
                f')'
                )


class Ad_Found_WatchLog(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT)
    bot = models.ForeignKey(Bots, on_delete=models.PROTECT)
    video_watched = models.ForeignKey(Videos, on_delete=models.PROTECT, related_name='video_watched')
    attempt = models.IntegerField(default=0)
    request_timestamp = models.BigIntegerField(default=0)
    ad_video = models.ForeignKey(Videos, on_delete=models.PROTECT, related_name='ad_video')
    ad_source = models.CharField(max_length=50, default='youtube')
    ad_duration = models.IntegerField(default=0)
    ad_skip_duration = models.IntegerField(default=0)
    ad_system = models.CharField(max_length=255, default='')
