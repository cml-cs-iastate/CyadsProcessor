import json
import numbers
from enum import Enum
from copy import deepcopy
import time
from typing import Optional, Union

def utc_timestamp_seconds():
    return int(time.time())


class InvalidBotCompletionStatus(Exception):
    '''Raised if an invalid bot completion status is given'''
    def __init__(self, message: str, status: str):
        self.message = message
        self.status = status


class BatchCompletionStatus(Enum):
    COMPLETE: str = "COMPLETE"
    ERROR: str = "ERROR"
    ABORTED: str = "ABORTED"

    def to_json(self) -> str:
        return self.value

    @staticmethod
    def from_json(kind) -> 'BatchCompletionStatus':
        return BatchCompletionStatus[kind]


class BotEvents(str, Enum):
    """Types of events that a bot spawner can send"""
    # A batch has started
    BATCH_STARTED = "batch_started"
    # A batch has completed
    BATCH_COMPLETED = "batch_completed"
    # A batch's data has been synced, and is ready for processing
    BATCH_SYNCED = "batch_synced"
    # Process all unprocessed batches which are synced
    PROCESS = "process"
    # Test event
    TEST = "test"


class BatchStarted:
    """Construction of, serialization, and deserialization of BatchStart messages"""
    def __init__(self,
                 bots_started: int,
                 hostname: str,
                 external_ip: str,
                 run_id: int,
                 host_hostname: str = None,
                 location: str = None,
                 timestamp: int = None,
                 video_list_size: int = 550):

        self.event = BotEvents.BATCH_STARTED
        self.bots_started = bots_started
        self.hostname: str = hostname
        if not isinstance(run_id, numbers.Integral):
            raise TypeError(f"{run_id} is {run_id.__class__}, not a type of int")
        self.run_id: int = run_id
        self.host_hostname: str = host_hostname
        self.external_ip: str = external_ip
        self.location: str = location
        self.video_list_size = video_list_size
        if timestamp is None:
            self.timestamp: int = utc_timestamp_seconds()
        else:
            self.timestamp: int = int(timestamp)
        if not isinstance(self.timestamp, numbers.Integral):
            raise ValueError(f"`timestamp` passed wasn't an int: was `{type(self.timestamp)}`")

    def has_location(self) -> bool:
        return self.location is not None and len(self.location) != 0

    @staticmethod
    def from_json(msg: str) -> 'BatchStarted':
        """Returns a BatchStarted from a trusted json BatchStarted message"""
        data: dict = json.loads(msg)
        event: Optional[str] = data.get("event")
        if event is None:
            raise KeyError("invalid msg, no event type")
        if event != BotEvents.BATCH_STARTED.value:
            raise AssertionError("Not a `batch started` msg")
        data.pop("event")
        video_list_size = data.get("video_list_size")
        if video_list_size is None:
            video_list_size = 550
        return BatchStarted(host_hostname=data["host_hostname"],
                            run_id=data["run_id"],
                            hostname=data["hostname"],
                            location=data["location"],
                            bots_started=data["bots_started"],
                            external_ip=data["external_ip"],
                            video_list_size=video_list_size)

    def to_json(self) -> str:
        """Return a reconstructable json BotStarted message"""
        return json.dumps(deepcopy(self.__dict__))


class BatchCompleted:

    def __init__(self,
                 hostname: str,
                 run_id: int,
                 external_ip: str,
                 status: BatchCompletionStatus,
                 ads_found: int,
                 requests: int,
                 host_hostname: str = None,
                 location: str = None,
                 timestamp: int = None,
                 bots_started: int = None,
                 video_list_size: int = 550):
        self.hostname: str = hostname
        if not isinstance(run_id, numbers.Integral):
            raise TypeError(f"{run_id} is {run_id.__class__}, not a type of int")
        self.event = BotEvents.BATCH_COMPLETED
        self.run_id: int = run_id
        self.host_hostname: str = host_hostname
        self.external_ip: str = external_ip
        self.location: str = location
        self.status: BatchCompletionStatus = status
        self.ads_found: int = ads_found
        self.requests: int = requests
        self.bots_started: int = bots_started
        self.timestamp: int = timestamp
        self.video_list_size = video_list_size
        if self.timestamp is None:
            self.timestamp = utc_timestamp_seconds()
        if not isinstance(self.timestamp, numbers.Integral):
            raise ValueError(f"`timestamp` passed wasn't an int: was `{type(timestamp)}`")

    def has_location(self) -> bool:
        return self.location is not None and len(self.location) != 0

    @staticmethod
    def completion_status(status: str) -> BatchCompletionStatus:
        """Translates text status into a usuable bot completion status code
        @raises InvalidBotCompletionStatus if status string is not a valid compleiton status"""
        try:
            return BatchCompletionStatus[status]
        except KeyError as e:
            raise InvalidBotCompletionStatus(f"`{status}` is an invalid bot completion status",
                                             status=str(status))

    @staticmethod
    def from_json(msg: str) -> 'BatchCompleted':
        data = json.loads(msg)
        event = data.get("event")
        timestamp = data.get("timestamp")
        bots = None
        if data.get("bots_in_batch") is not None:
            bots = data.get("bots_in_batch")

        video_list_size = data.get("video_list_size")
        if video_list_size is None:
            video_list_size = 550

        if timestamp is None:
            raise ValueError("invalid msg, no creation timestamp")
        if event is None:
            raise ValueError("invalid msg, no event type")
        if event != BotEvents.BATCH_COMPLETED.value:
            raise AssertionError("Not a `batch completed` msg")
        data.pop("event")
        status: BatchCompletionStatus = BatchCompleted.completion_status(data["status"])
        data["status"] = status
        return BatchCompleted(host_hostname=data["host_hostname"],
                              run_id=data["run_id"],
                              hostname=data["hostname"],
                              location=data["location"],
                              status=data["status"],
                              timestamp=data["timestamp"],
                              external_ip=data["external_ip"],
                              ads_found=data["ads_found"],
                              requests=data["requests"],
                              bots_started=bots,
                              video_list_size=video_list_size)

    def to_dict(self) -> dict:
        return deepcopy(self.__dict__)

    def to_json(self) -> str:
        # The dict must be copied, or else it modifies the object dictionary in place later on
        unfinished: dict = deepcopy(self.__dict__)
        # override `status` entry with value from status enum
        # Otherwise the value is <BatchCompletion.ERROR: 'ERROR'> instead of 'ERROR'
        unfinished["status"] = self.status.value
        return json.dumps(unfinished)


class BatchSyncStatus(Enum):
    COMPLETE: str = "COMPLETE"
    ERROR: str = "ERROR"

    @staticmethod
    def from_json(kind: str) -> 'BatchSyncStatus':
        return BatchSyncStatus[kind]

    def to_json(self) -> str:
        return json.dumps({"kind": self.value})


class BatchSyncComplete:
    def __init__(self):
        self.kind = BatchSyncStatus.COMPLETE

    @staticmethod
    def from_json(info: str) -> 'BatchSyncComplete':
        return BatchSyncComplete()

    def to_json(self) -> str:
        return self.kind.to_json()


class BatchSyncErrMsg:
    def __init__(self, returncode: int, stdout: str, stderr: str):
        self.returncode: int = returncode
        self.stdout: str = stdout
        self.stderr: str = stderr

    def to_dict(self):
        return deepcopy(self.__dict__)

    def to_json(self) -> str :
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(info: str) -> 'BatchSyncErrMsg':
        data: dict = json.loads(info)
        return BatchSyncErrMsg(returncode=data["returncode"], stdout=data["stderr"], stderr=data["stderr"])

class BatchSyncError:
    def __init__(self, err_info: BatchSyncErrMsg):
        self.kind: BatchSyncStatus = BatchSyncStatus.ERROR
        self.details: BatchSyncErrMsg = err_info

    @staticmethod
    def from_json(info: str) -> 'BatchSyncError':
        data = json.loads(info)
        err_msg: BatchSyncErrMsg = BatchSyncErrMsg.from_json(data["details"])
        return BatchSyncError(err_info=err_msg)

    def to_json(self) -> str:
        output = {}
        output["kind"] = self.kind.value
        output["details"] = json.loads(self.details.to_json())
        return json.dumps(output)


class BatchSynced:

    def __init__(self, batch_info: BatchCompleted, sync_result: Union[BatchSyncComplete, BatchSyncError]):
        self.kind: BatchSyncStatus = sync_result.kind
        self.event: BotEvents = BotEvents.BATCH_SYNCED
        self.batch_info = batch_info
        self.data: Union[BatchSyncComplete, BatchSyncError] = sync_result

    def to_json(self) -> str:
        text = {}
        text["event"] = self.event.value
        text["batch_info"] = json.loads(self.batch_info.to_json())
        text["kind"] = self.kind.value
        text["data"] = json.loads(self.data.to_json())
        return json.dumps(text)

    @staticmethod
    def from_json(info: str) -> 'BatchSynced':
        data: dict = json.loads(info)
        batch_info: BatchCompleted = BatchCompleted.from_json(json.dumps(data["batch_info"]))
        kind: BatchSyncStatus = BatchSyncStatus.from_json(data["kind"])
        if kind == BatchSyncStatus.COMPLETE:
            sync_result: BatchSyncComplete = BatchSyncComplete.from_json(info)
        elif kind == BatchSyncStatus.ERROR:
            sync_result = BatchSyncError.from_json(data["data"])
        else:
            raise Exception(f"Invalid BatchSyncStatus: {kind}")

        return BatchSynced(batch_info=batch_info,
                           sync_result=sync_result)


class BatchPayload:

    @staticmethod
    def get_payload_event(msg):
        data = json.loads(msg)
        event = data.get("event")
        try:
            return BotEvents(event)
        except ValueError:
            raise ValueError(f"invalid msg, no BotEvent type: {event}")
