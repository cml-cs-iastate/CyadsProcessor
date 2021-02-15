import datetime
from collections import namedtuple

from django.db.models import Sum, Count, Func, DateTimeField, Count
from django.db.models.functions import TruncDate
from django.shortcuts import render

from processor.models import Batch, Constants, Ad_Found_WatchLog, Videos, AdFile


def index(request):
    return render(None, 'new_index.html')

def completed(request):
    return render(None, "completed.html")


from processor.views import BatchViewSet

def running(request):

    running_batches_with_day = BatchViewSet.batches_with_datetime().filter(status=Constants.BATCH_RUNNING).annotate(start_day=TruncDate('start_datetime'))

    batches_count_per_day = running_batches_with_day.values("start_day").annotate(count=Count('start_day')).order_by('start_day')
    number_running_locations = running_batches_with_day.values("location", "location__state_name").annotate(count=Count('location')).order_by()

    return render(request, "running.html", {
        "running_batches": running_batches_with_day,
        "running_by_location": number_running_locations,
        "batches_count_by_day": batches_count_per_day,
    })


def namedtuplefetchall(cursor):
    """Return all rows from a cursor as a namedtuple"""
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

from dataclasses import dataclass

@dataclass
class TableInfo:
    table_name: str
    record_count: int


def database_mb_view(request):
    # Gather record counts of important columns in the DB
    motherbrain_tables: [TableInfo] = [
        TableInfo(Ad_Found_WatchLog._meta.db_table, Ad_Found_WatchLog.objects.all().count()),
        TableInfo(Videos._meta.db_table, Videos.objects.all().count()),
        TableInfo(AdFile._meta.db_table, AdFile.objects.all().count()),
    ]

    gcp_tables: [TableInfo] = [
        TableInfo(Ad_Found_WatchLog._meta.db_table, Ad_Found_WatchLog.objects.using('ad_extension').all().count()),
        TableInfo(Videos._meta.db_table, Videos.objects.using('ad_extension').all().count()),
        TableInfo(AdFile._meta.db_table, AdFile.objects.using('ad_extension').all().count()),
    ]

    return render(request, 'database_mb.html', {
        "mb_tables_info": motherbrain_tables,
        "gcp_copy_tables_info": gcp_tables,
    })
