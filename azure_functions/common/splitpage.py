"""Split Page Class
"""


class SplitPage:
    """
    A section of a page that has been split into a smaller chunk.
    """

    def __init__(
        self,
        page_num: int,
        text: str,
    ):
        self.page_num = page_num
        self.text = text
