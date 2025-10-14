"""Section class for storing a section of a page
in a search service."""

from typing import Optional

from common.splitpage import SplitPage
from common.shared import File


class Section:
    """
    A section of a page that is stored in a search service. These sections are
    used as context by Azure OpenAI service
    """

    def __init__(
        self,
        split_page: SplitPage,
        content: File,
        category: Optional[str] = None,
    ):
        self.split_page = split_page
        self.content = content
        self.category = category
