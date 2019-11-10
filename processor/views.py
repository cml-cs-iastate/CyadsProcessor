from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

from .BatchProcessor import BatchProcessor
from processor.models import Batch
from processor.exceptions import BatchNotSynced


def reprocess(request, batch_id) -> HttpResponse:
    processor = BatchProcessor()
    # Obviously, the batch must exist first to reprocess it
    batch = Batch.objects.get(pk=batch_id)

    # However, we won't process a batch unless it is synced
    if not batch.synced:
        raise BatchNotSynced(f"Cannot process unless synced: batch {batch.id}")

    batch_synced = batch.into_batch_synced()
    processor.process_batch_synced(batch_synced)
    return HttpResponse(f"processing batch: {batch_id}")