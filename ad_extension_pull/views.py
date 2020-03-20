from .models import ProcessorAddsViaExtension
from processor.models import Videos
from processor.BatchProcessor import BatchProcessor
from django.http import HttpResponse



from structlog import get_logger
logger = get_logger()


def view_process_videos_collected_from_extension(request):
    process_videos_collected_from_extension()
    return HttpResponse("processed ad extension videos")


def process_videos_collected_from_extension():
    unprocessed_extension_vids = ProcessorAddsViaExtension.objects.filter(processed=False)

    unprocessed_extension_log: ProcessorAddsViaExtension
    for unprocessed_extension_log in unprocessed_extension_vids:
        vid_id = unprocessed_extension_log.ad_video_id
        batch_processor = BatchProcessor()
        batch_processor.save_video_metadata([vid_id], is_ad=True)
        unprocessed_extension_log.processed = True
        unprocessed_extension_log.save()
        vid_db_id = Videos.objects.get(url=vid_id)
        logger.info("processed extension video", url=vid_id, vid_db_id=vid_db_id)
