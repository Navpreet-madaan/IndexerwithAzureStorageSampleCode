import os
from datetime import datetime, timezone


DATEIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class Summary:

    def __init__(
        self,
        config_name,
    ):

        self.activity: str = "preprocess"
        self.build_id: str = os.getenv(
            "BUILD_ID",
            "Local Build",
        )
        self.config_name: str = config_name
        self.start_time: datetime = datetime.now(timezone.utc)
        self.end_time: datetime = None

        self.new_file: list[str] = []
        self.updated_file: list[str] = []
        self.deleted_file: list[str] = []
        self.unchanged_file: list[str] = []

        self.closed_reason: str = None
        self.log: str = None

    def get_metrics(
        self,
    ):
        return {
            "build_id": self.build_id,
            "activity": self.activity,
            "config_name": self.config_name,
            "start_time": self.start_time.strftime(DATEIME_FORMAT),
            "end_time": self.end_time.strftime(DATEIME_FORMAT),
            "duration": (self.end_time - self.start_time).total_seconds(),
            "new": len(self.new_file),
            "updated": len(self.updated_file),
            "deleted": len(self.deleted_file),
            "unchanged": len(self.unchanged_file),
            "log": self.log,
        }

    def get_full_log(
        self,
    ):
        _full_log = {}
        _full_log.update(self.get_metrics())
        _full_log.update(
            {
                "new_files": self.new_file,
                "updated_files": self.updated_file,
                "deleted_files": self.deleted_file,
                "unchanged_files": self.unchanged_file,
            }
        )
        return _full_log
