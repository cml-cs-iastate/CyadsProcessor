from .models import ProcessorAddsViaExtension
from processor.models import Videos
from processor.BatchProcessor import BatchProcessor
from structlog import get_logger
logger = get_logger()


def process_videos_collected_from_extension():
    unprocessed_extension_vids = ProcessorAddsViaExtension.objects.filter(processed=False)

    unproccessed_extension_log: ProcessorAddsViaExtension
    for unproccessed_extension_log in unprocessed_extension_vids:
        vid_id = unproccessed_extension_log.ad_video_id
        video: Videos
        video, created = Videos.objects.get_or_create(url=vid_id)

        if not video.checked:
            batch_processor = BatchProcessor()
            batch_processor.save_video_metadata([vid_id], is_ad=True)
        unproccessed_extension_log.processed = True
        unproccessed_extension_log.save()
        logger.info("proccessed extesion video", url=vid_id, db_vid_id=video.id)
