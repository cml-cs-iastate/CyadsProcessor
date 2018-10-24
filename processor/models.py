from django.db import models


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

    def get_state_abb(self,state):
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
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
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


class Bots(models.Model):
    name = models.CharField(max_length=100)


class Categories(models.Model):
    cat_id = models.IntegerField()
    name = models.CharField(max_length=100)


class Channels(models.Model):
    channel_id = models.TextField()
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, default='')


class Videos(models.Model):
    url = models.TextField()
    title = models.TextField(default='')
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channels, on_delete=models.CASCADE)
    description = models.TextField(default='')
    keywords = models.TextField(default='')
    watched_as_ad = models.IntegerField(default=0)
    watched_as_video = models.IntegerField(default=0)


class Ad_Found_WatchLog(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    bot = models.ForeignKey(Bots, on_delete=models.CASCADE)
    video_watched = models.ForeignKey(Videos, on_delete=models.CASCADE, related_name='video_watched')
    attempt = models.IntegerField(default=0)
    request_timestamp = models.BigIntegerField(default=0)
    ad_video = models.ForeignKey(Videos, on_delete=models.CASCADE, related_name='ad_video')
    ad_source = models.CharField(max_length=50, default='youtube')
    ad_duration = models.IntegerField(default=0)
    ad_skip_duration = models.IntegerField(default=0)
    ad_system = models.CharField(max_length=255, default='')


# class Ads(models.Model):
#     watch_log = models.ForeignKey(AdFoundWatchLog, on_delete=models.CASCADE)
#     video = models.ForeignKey(Videos, on_delete=models.CASCADE)
#     source = models.CharField(max_length=50,default='youtube')
#     ad_duration = models.IntegerField(default=0)
#     skip_duration = models.IntegerField(default=0)
#     system = models.CharField(max_length=255,default='')




