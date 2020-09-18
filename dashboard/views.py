import datetime

from django.db.models import Sum, Count, Func, DateTimeField
from django.db.models.functions import TruncDate
from django.shortcuts import render

from processor.models import Batch, Constants, Ad_Found_WatchLog


def index(request):
    now = datetime.datetime.now()
    html = f"<html><body>It is now {now}.</body></html>"

    batches_still_running = Batch.objects.filter(status=Constants.BATCH_RUNNING).count()

    batches_per_day: int = Batch.objects.filter(status=Constants.BATCH_RUNNING).values("start_timestamp")\
        .annotate(day=Func('start_timestamp', function="FROM_UNIXTIME", output_field=DateTimeField()))\
        .values('day').annotate(uniq_day=TruncDate('day'))\
        .values('uniq_day').distinct().count()

    number_running_locations: int = Batch.objects.filter(status=Constants.BATCH_RUNNING).values("location_id").distinct().count()

    return render(request, 'new_index.html', {"batches_running": batches_still_running,
                                              "dates_still_running": batches_per_day,
                                              "locations_number_running": number_running_locations,
                                              })


def completed(request):
    return render(None, "completed.html")
