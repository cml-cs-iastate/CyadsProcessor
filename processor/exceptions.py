from typing import List

class BatchNotSynced(Exception):
    pass


from typing import List
from pathlib import Path


class WatchLogAdExtractionException(Exception):
    def __init__(self, error_files: List[Path] = None, msg="Some ad files had no info", *args, **kwargs):
        self.error_files = error_files
        if error_files is None:
            self.error_files = []
        super().__init__(msg, *args)

    def __str__(self):
        num_errors = len(self.error_files)
        return f"{num_errors} ad file(s) had no ad data inside"
