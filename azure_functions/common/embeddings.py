"Class for emeddings"
import logging
from abc import ABC
from typing import List
import tiktoken
from bs4 import BeautifulSoup, FeatureNotFound

from langchain.text_splitter import MarkdownTextSplitter
from openai import OpenAI, RateLimitError
from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from common.embeddingsbatch import EmbeddingBatch


class OpenAIEmbeddings(ABC):
    """
    Contains common logic across both OpenAI and Azure OpenAI embedding
    Can split source text into batches for more efficient embedding calls
    """

    def __init__(
        self,
        open_ai_model_name: str,
        batch_aoai_model: str,
        disable_batch: bool = False,
        verbose: bool = False,
    ):
        self.open_ai_model_name = open_ai_model_name
        self.disable_batch = disable_batch
        self.verbose = verbose
        self.batch_aoai_model = batch_aoai_model

    def create_client(self) -> OpenAI:
        "Client for Open AI"
        raise NotImplementedError

    def before_retry_sleep(self, _):
        "Sleep  before retrying"
        if self.verbose:
            logging.debug(
                "Rate limited on the OpenAI embeddings API, before retrying..."
            )

    def calculate_token_length(self, text: str):
        "Calculate Token Length"
        encoding = tiktoken.encoding_for_model(self.open_ai_model_name)
        return len(encoding.encode(text))

    def split_text_to_batches(self, texts: List[str]) -> List[EmbeddingBatch]:
        "Split Text into batches"
        batch_info = self.batch_aoai_model.get(self.open_ai_model_name)
        batch_token_limit = batch_info["token_limit"]
        batch_max_size = batch_info["max_batch_size"]
        batches: List[EmbeddingBatch] = []
        batch: List[str] = []
        batch_token_length = 0
        for text in texts:
            text_token_length = self.calculate_token_length(text)
            if (
                batch_token_length + text_token_length >= batch_token_limit
                and len(batch) > 0
            ):
                batches.append(EmbeddingBatch(batch, batch_token_length))
                batch = []
                batch_token_length = 0

            batch.append(text)
            batch_token_length = batch_token_length + text_token_length
            if len(batch) == batch_max_size:
                batches.append(EmbeddingBatch(batch, batch_token_length))
                batch = []
                batch_token_length = 0

        if len(batch) > 0:
            batches.append(EmbeddingBatch(batch, batch_token_length))

        return batches

    # Creating Emedding batch with max limit of configurable value
    # (1000 default one)
    def create_embedding_batch(self, texts: List[str]) -> List[List[float]]:
        "Creating Emedding batch with max limit of configurable value"
        batches = self.split_text_to_batches(texts)
        embeddings = []
        client = self.create_client()
        for batch in batches:
            for attempt in Retrying(
                retry=retry_if_exception_type(RateLimitError),
                wait=wait_random_exponential(min=15, max=60),
                stop=stop_after_attempt(15),
                before_sleep=self.before_retry_sleep,
            ):
                with attempt:
                    emb_response = client.embeddings.create(
                        model=self.open_ai_model_name, input=batch.texts
                    )
                    embeddings.extend([data.embedding for data in emb_response.data])
                    # return generated emeddings with Azure Open AI vectors
        return embeddings

    # Create a single emeddings out of the batch
    def create_embedding_single(self, text: str) -> List[float]:
        "Create a single emeddings out of the batch"
        client = self.create_client()
        for attempt in Retrying(
            retry=retry_if_exception_type(RateLimitError),
            wait=wait_random_exponential(min=15, max=60),
            stop=stop_after_attempt(15),
            before_sleep=self.before_retry_sleep,
        ):
            with attempt:
                emb_response = client.embeddings.create(
                    model=self.open_ai_model_name, input=text
                )
        # return single emedding
        return emb_response.data[0].embedding

    # create emdding method which will cal internally batch and single
    # emedding model
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        "create emdding method which will cal internally batch and single"
        if not self.disable_batch and self.open_ai_model_name in self.batch_aoai_model:
            return self.create_embedding_batch(texts)

        return [self.create_embedding_single(text) for text in texts]

    def split_text_with_metadata(self, contentindexdata, container_path):
        "Process the contentindexdata HTML content"
        try:
            # Process the contentindexdata HTML content
            soup = BeautifulSoup(contentindexdata, "html.parser")
            html = str(soup)
        except FeatureNotFound:
            html = contentindexdata
        # Initialize the MarkdownTextSplitter
        splitter = MarkdownTextSplitter()
        documents = []
        if contentindexdata:
            splits = splitter.split_text(html)
            for split in splits:
                _results = self.create_embedding_single(split)
                document = [
                    {
                        "content": split,
                        "pagesource": container_path,
                        "embedding": _results,
                    }
                ]
                documents.extend(document)
        return documents
