import datetime
from collections import namedtuple

from django.db import connection, connections
from django.db.models import Sum, Count, Func, DateTimeField, Count
from django.db.models.functions import TruncDate
from django.shortcuts import render

from processor.models import Batch, Constants, Ad_Found_WatchLog


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


def database_mb_view(request):

    ad_views_motherbrain = Ad_Found_WatchLog.objects.all().count()
    ad_views_gcp_copy = Ad_Found_WatchLog.objects.using('ad_extension').all().count()

    query = "SELECT table_name AS table_name, round(((data_length + index_length) / 1024 / 1024), 2) AS data_size_mb , TABLE_ROWS as rows_estimate FROM information_schema.TABLES WHERE table_schema = 'cyads_processor' order by table_schema asc;"
    with connections['default'].cursor() as cursor:
        cursor.execute(query)
        motherbrain_table_info = namedtuplefetchall(cursor)

    with connections['ad_extension'].cursor() as cursor:
        cursor.execute(query)
        gcp_copy_table_info = namedtuplefetchall(cursor)

    return render(request, 'database_mb.html', {
        "mb_tables_info": motherbrain_table_info,
        "gcp_copy_tables_info": gcp_copy_table_info,
        "ad_views_mb": ad_views_motherbrain,
        "ad_views_gcp_copy": ad_views_gcp_copy,
    })
