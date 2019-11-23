from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

# Create your views here.

from .BatchProcessor import BatchProcessor
from processor.models import Batch
from processor.exceptions import BatchNotSynced
from datetime import datetime


def process_all(reuqest: HttpRequest) -> HttpResponse:
    batch_processor = BatchProcessor()
    batch_processor.process_all_unprocessed_but_synced()
    return HttpResponse("processing all unprocessed batches.", status=202)


def process(request: HttpRequest, batch_id: int, force: bool = False) -> HttpResponse:
    """Process a batch if it hasn't already been processed"""
    _start_bench = datetime.utcnow()
    processor = BatchProcessor()
    # Obviously, the batch must exist first to reprocess it
    batch = Batch.objects.get(pk=batch_id)

    # However, we won't process a batch unless it is synced
    if not batch.synced:
        raise BatchNotSynced(f"Cannot process unless synced: batch {batch.id}")

    # Selectively decide if forced
    if force or not batch.processed:
        # Clear out previous remarks
        batch.save()
        batch_synced = batch.into_batch_synced()
        processor.process_batch_synced(batch_synced)
    else:
        return HttpResponse(f"Batch {batch_id} already processed. Used `force` to reprocess")
    _end_bench = datetime.utcnow()
    _elapsed_bench = _end_bench - _start_bench

    return HttpResponse(f"Finished processing batch: {batch_id} in {_elapsed_bench.total_seconds()} seconds")


def test(request, number: int):
    return HttpResponse(f"Server active: Got number: {number}")
