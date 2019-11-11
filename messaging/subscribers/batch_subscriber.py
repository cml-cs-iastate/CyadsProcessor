import logging

from google.cloud import pubsub
from messaging.payloads.BatchPayload import BatchPayload
from processor.BatchProcessor import BatchProcessor


class BatchSubscriber:

    logger = logging.getLogger(__name__)

    def __init__(self,project_id, topic, subscription):

        self.project_id = project_id
        self.topic = topic
        self.subscription = subscription

    def subscribe_topic(self):
        subscriber = pubsub.SubscriberClient()
        subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(project_id=self.project_id,
                                                                               sub=self.subscription)

        try:
            future = subscriber.subscribe(subscription_name, self.callback)
            # future.result()
        except Exception as e:
            self.logger.error("Not Able to subscribe ro the topic ", str(e))
            raise e

        #future.result()
        self.logger.info("=======================================================")
        self.logger.info("=     S U B S C R I B E R  1.6                        =")
        self.logger.info("=                                                     =")
        self.logger.info("=         S T A R T E D                               =")
        self.logger.info("=                                                     =")
        self.logger.info("=======================================================")

    def callback(self,message):
        self.logger.info("Received the message : ")
        self.logger.info(message.data)
        try:
            event = BatchPayload.get_payload_event(message.data)
            self.logger.info("Received event : " + str(event))
        except Exception as e:
            self.logger.error("Invalid Payload")
            self.logger.exception(str(e))
            message.ack()
            return
        try:
            processor = BatchProcessor()
            # ack a call to process all batches incase of continuous exceptions and long running tasks
            if event == event.PROCESS:
                message.ack()
            processor.process(batch_data=message.data, event=event)
            message.ack()
        except Exception as e:
            self.logger.error("Got error while processing ")
            self.logger.exception(str(e))
            message.ack()
