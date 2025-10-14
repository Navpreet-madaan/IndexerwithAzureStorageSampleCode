"Batch embeddings"
from typing import List


class EmbeddingBatch:
    """
    Represents a batch of text that is going to be embedded
    """

    def __init__(
        self,
        texts: List[str],
        token_length: int,
    ):
        self.texts = texts
        self.token_length = token_length
