from django.db.models import Sum, Count
from django.shortcuts import render

from processor.models import Batch, Constants


def index(request):

    running_batch = Batch.objects.filter(status=Constants.BATCH_RUNNING).order_by('start_timestamp')
    completed_batch = Batch.objects.filter(status=Constants.BATCH_COMPLETED).order_by('start_timestamp')
    location_stats = Batch.objects.values('location__state_name').filter(status=Constants.BATCH_COMPLETED)
    location_stats = location_stats.annotate(total_batches=Count('id'),
                                             total_ads=Sum('total_ads_found'),
                                             total_requests=Sum('total_requests')).order_by('-total_batches')
    return render(request,'index.html', {'running_batch': running_batch,
                                         'completed_batch': completed_batch,
                                         'location_stats': location_stats}
                  )