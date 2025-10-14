"""
This class is a connector to integrate with the Speedperform API.
"""

import json

from datetime import datetime
from dataclasses import dataclass

TIMEOUT: int = 30


class ArticleJSONDecoder(json.JSONDecoder):
    """Article JSON Decoder

    Args:
        json (_type_): json object
    """

    def __init__(self):
        json.JSONDecoder.__init__(
            self,
            object_hook=ArticleJSONDecoder.from_dict,
        )

    @staticmethod
    def from_dict(d):
        """
        Convert the dictionary item to an object
        """
        _id = d["id"]
        _revision_id = d["revisionId"]
        _last_modified = datetime.strptime(
            d["lastModified"],
            "%Y-%m-%dT%H:%M:%SZ",
        )

        _article_info = ArticleInfo(
            id=_id,
            revision_id=str(_revision_id),
            type=d["type"],
            title=d["title"],
            description=d["description"],
            last_modified=_last_modified,
            status=d["status"],
            public_link=d["publicLink"],
        )
        return _article_info


@dataclass
class ArticleInfo(object):
    """
    A Speed perform article with information about it
    """

    id: str
    revision_id: str
    type: str
    title: str
    description: str
    last_modified: datetime
    status: str
    public_link: str

    @classmethod
    def from_json(
        cls,
        json_str,
    ):
        """
        Convert the json to object
        """
        _articles_info = json.loads(
            json_str,
            cls=ArticleJSONDecoder,
        )
        return _articles_info
