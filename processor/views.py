from django.db.models import Func, DateTimeField
from django.http import HttpResponse, HttpRequest

# Create your views here.
from processor.models import Videos, Constants
from .BatchProcessor import BatchProcessor
from processor.models import Batch
from rest_framework import viewsets
from .serializers import BatchSerializer

from datetime import datetime

import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory

structlog.configure(logger_factory=LoggerFactory())
logger = get_logger()


def view_gather_video_info_catchup(request):
    gather_video_info_catchup()
    return HttpResponse("finished gatching up videos not downloaded")


def gather_video_info_catchup():
    video: Videos
    for video in Videos.objects.filter(checked=False, watched_as_ad__gte=0):
        batch_processor = BatchProcessor()
        batch_processor.save_video_metadata([video.url], is_ad=True)
        vid_db_id = Videos.objects.get(url=vid_id)
        logger.info("processed extension video", url=vid_id, vid_db_id=vid_db_id)


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
        raise HttpResponse(f"Cannot process unless synced: batch {batch.id}", status=400)

    # Reprocess if forced
    if force:
        # Clear out previous remarks
        batch.remarks = ""
        batch.processed = False
        batch.save()

    if not batch.processed:
        logger.info("processing batch", batch_id=batch.id)
        batch_synced = batch.into_batch_synced()
        processor.process_batch_synced(batch_synced)

        _end_bench = datetime.utcnow()
        _elapsed_bench = _end_bench - _start_bench
        logger.info("proccessed batch", batch_id=batch.id, time_taken=_elapsed_bench.total_seconds())
    else:
        return HttpResponse(f"Batch {batch_id} already processed. Used `force` to reprocess")

    return HttpResponse(f"Finished processing batch: {batch_id} in {_elapsed_bench.total_seconds()} seconds")


def test(request, number: int):
    logger.info("test request", number=number)
    return HttpResponse(f"Server active: Got number: {number}")


def test_error(request, err_msg: str):
    raise Exception(f"test error reporting - msg: {err_msg}")


class BatchViewSet(viewsets.ModelViewSet):

    def batches_with_datetime():
        # .filter(status=Constants.BATCH_COMPLETED)
        return Batch.objects.select_related('location').all().annotate(
            start_datetime=Func('start_timestamp', function="FROM_UNIXTIME", output_field=DateTimeField()),
            completed_datetime=Func(
                'completed_timestamp',
                function="FROM_UNIXTIME",
                output_field=DateTimeField()),
            )

    queryset = batches_with_datetime()
    serializer_class = BatchSerializer
