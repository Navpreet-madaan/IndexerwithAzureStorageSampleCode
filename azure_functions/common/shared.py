"""Represents a file stored either locally or in a data lake storage account
    Returns:
        _type_: returns the file
"""

import os
import re
import base64

from typing import IO, Optional


class File:
    """
    Represents a file stored either locally or in a data lake storage account
    This file might contain access control information about which users or
    groups can access it
    """

    def __init__(
        self,
        content: IO,
        acls: Optional[dict[str, list]] = None,
    ):
        self.content = content
        self.acls = acls or {}

    def filename(self):
        "file Name"
        return os.path.basename(self.content.name)

    def filename_to_id(self):
        "File Name to ID"
        filename_ascii = re.sub("[^0-9a-zA-Z_-]", "_", self.filename())
        filename_hash = base64.b16encode(self.filename().encode("utf-8")).decode(
            "ascii"
        )
        return f"file-{filename_ascii}-{filename_hash}"

    def close(self):
        "closing the File"
        if self.content:
            self.content.close()
