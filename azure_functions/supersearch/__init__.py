"""
Supersearch processing module
"""

import base64
import concurrent.futures
import hashlib
import json
import logging
import os
import time
import uuid

from azure.identity import DefaultAzureCredential
from common import KeyVault
from common.handlers import KeyVaultHandler
from common.openaiembeddingservice import AzureOpenAIEmbeddingService
from helpers.configmapper import ConfigMapper
from helpers.searchmanager import SearchManager

from supersearch.articleinfo import ArticleInfo
from supersearch.contentparser import ContentParser
from supersearch.customexception import CustomException
from supersearch.metadata import Document, DocumentManager
from supersearch.qgen import QuestionGenerator
from supersearch.spdpfm import SpeedPerformAPI

ARTICLE_IS_ONLINE = "Online"
SUPERSEARCH_INDEX_NAME = "supersearch"
DEFAULT_CLASSIFICATION = "Unclassfied"
MAX_WORKERS = 5
MAX_ITEMS = MAX_WORKERS * 4

# someone is resetting this in the imports.
logging.basicConfig(level=logging.INFO)


class SuperSearch:
    """
    Represents a super search.
    """

    def __init__(self):
        self._index_name = SUPERSEARCH_INDEX_NAME
        self._speed_perform_api = SpeedPerformAPI()
        self._content_parser = ContentParser()
        _credential = DefaultAzureCredential()
        _key_vault_handler = KeyVaultHandler()
        _open_ai_service = _key_vault_handler.get_secret(
            secret_name=KeyVault.open_ai_service_secret_name,
        )
        _search_service = _key_vault_handler.get_secret(
            secret_name=KeyVault.azure_ai_search_service,
        )
        _index_name = self._index_name

        _config_mapper = ConfigMapper()
        self._embedding_service = AzureOpenAIEmbeddingService(
            open_ai_service=_open_ai_service,
            credential=_credential,
            config_mapper=_config_mapper,
        )
        self._search_manager: SearchManager = SearchManager(
            _searchservice=_search_service,
            _index_name=_index_name,
            _credential=_credential,
            config_mapper=_config_mapper,
        )

        self._question_generator = QuestionGenerator()

        _build_id = os.getenv("BUILD_ID", "Local Build")
        logging.info(
            "Initialized super search for build id %s",
            _build_id,
        )

    def create_index(self):
        """Create the index if it does not exist."""
        _search_manager: SearchManager = self._search_manager
        _index_name = self._index_name
        _search_manager._create_index(_index_name)  # noqa: 501
        logging.info("Index %s created successfully", _index_name)

    def index_article(
        self,
        article_info: ArticleInfo,
        op: str,
    ):
        """Index an article.

        Args:
            article_info (ArticleInfo): The article to index.

        Raises:
            CustomException: If the article cannot be indexed.
        """
        _document_id = None
        _result = None
        try:
            _metadata: Document = self._map(article_info, None)
            _document_id = _metadata.id
            _index_name = self._index_name

            st = time.time()
            _speed_perform_api = self._speed_perform_api
            _content, _url = _speed_perform_api.get(
                article_id=_document_id,
            )
            et = time.time()
            logging.info(
                "Time taken to get speedperform article %s with length %s is %s",
                _document_id,
                len(_content),
                et - st,
            )

            _metadata.checksum = self._get_checksum(_content)

            _html_content = json.loads(json.loads(_content)["Html"])
            _parsed_html_list = self._content_parser.extract_html_content(_html_content)

            _document = None
            for _parsed_content in _parsed_html_list:
                st = time.time()
                _embedding_service: AzureOpenAIEmbeddingService = (
                    self._embedding_service
                )  # noqa: 501
                _embedding = _embedding_service.create_embedding_single(
                    text=_parsed_content,
                )
                et = time.time()
                logging.info(
                    "Time taken to get embedding for article %s is %s",
                    _document_id,
                    et - st,
                )

                _generated_question = self._question_generator.generate(
                    content=_parsed_content,
                )
                _document = {
                    "id": str(uuid.uuid4()),
                    "documentId": str(_document_id),
                    "content": _parsed_content,
                    "embedding": _embedding,
                    "title": article_info.title,
                    "url": str(
                        {
                            "url": article_info.public_link,
                            "question": _generated_question,
                        }
                    ),
                    "filepath": _url,
                }

                _search_manager: SearchManager = self._search_manager
                st = time.time()
                _response = _search_manager.add(  # noqa: F841
                    index_name=_index_name,
                    doc_id=str(_metadata.id),
                    index_update=op == "update",
                    documents=[_document],
                )
                et = time.time()
                logging.info(
                    "Time taken to index article %s is %s",
                    _document_id,
                    et - st,
                )

            if len(_parsed_html_list) == 0:
                logging.info(
                    "No html content found for article %s",
                    _document_id,
                )

            _document_manager = DocumentManager()
            st = time.time()
            _document_manager.save(_metadata)
            et = time.time()
            logging.info(
                "Time taken to update db for %s is %s",
                _document_id,
                et - st,
            )
            _result = {
                "id": _document_id,
                "status": "Success",
            }
        except Exception as e:
            _result = {
                "id": _document_id,
                "status": "Failed",
                "error": e,
            }
        return _result

    def get_speed_perform_list(
        self,
    ):
        """Get the list of articles from the speed perform API."""
        _speed_perform_api = self._speed_perform_api
        _speed_perform_list = _speed_perform_api.list()
        return _speed_perform_list

    def _map(
        self,
        speed_perform_item: ArticleInfo,
        metadata_item: Document,
    ):
        _metadata_item: Document = None
        if metadata_item:
            _metadata_item = metadata_item
        else:
            _metadata_item = Document()
        _metadata_item.id = speed_perform_item.id
        _metadata_item.name = speed_perform_item.title
        _metadata_item.version = speed_perform_item.revision_id
        _metadata_item.last_modified = speed_perform_item.last_modified
        _metadata_item.status = speed_perform_item.status
        return _metadata_item

    def get_metadata_list(
        self,
    ):
        """get metadata list

        Returns:
            _type_: returns the metadata list
        """
        _document_manager = DocumentManager()
        _metadata_list = _document_manager.list()
        return _metadata_list

    def get_delta(
        self,
        speed_perform_list: list,
        metadata_list: list,
    ):
        """Get the delta between the speed
        perform list and the metadata list."""
        _items_to_add = []
        _items_to_update = []
        _items_to_delete = []
        _items_not_online = []
        _speed_perform_item: ArticleInfo
        _metadata_item: Document
        for _speed_perform_item in speed_perform_list:
            _item_exists: bool = False
            for _metadata_item in metadata_list:
                if _speed_perform_item.id == _metadata_item.id:
                    # if the item is online and has a
                    # different version or last modified date
                    if _speed_perform_item.status == ARTICLE_IS_ONLINE and (
                        _speed_perform_item.revision_id
                        != _metadata_item.version  # noqa: E501
                        or _speed_perform_item.last_modified
                        != _metadata_item.last_modified
                    ):
                        # item is still online and needs updating
                        _items_to_update.append(_speed_perform_item)
                    elif (
                        _speed_perform_item.status != ARTICLE_IS_ONLINE
                        and _metadata_item.status == ARTICLE_IS_ONLINE
                    ):
                        # item is offline and should be removed
                        _item_to_delete: Document = self._map(
                            _speed_perform_item,
                            _metadata_item,
                        )
                        _items_to_delete.append(_item_to_delete)
                    _item_exists = True
                    break
            if not _item_exists:
                # add only items that are marked Online
                if _speed_perform_item.status == ARTICLE_IS_ONLINE:
                    _items_to_add.append(_speed_perform_item)
            if _speed_perform_item.status != ARTICLE_IS_ONLINE:
                _items_not_online.append(_speed_perform_item)

        # If there are items in the metadata list
        # that are not in the speed perform list, mark them as offline
        for _metadata_item in metadata_list:
            _item_exists = False
            for _speed_perform_item in speed_perform_list:
                if _metadata_item.id == _speed_perform_item.id:
                    _item_exists = True
                    break
            if not _item_exists and _metadata_item.status == ARTICLE_IS_ONLINE:
                _metadata_item.status = "Offline"
                _items_to_delete.append(_metadata_item)
        return (
            _items_to_add,
            _items_to_update,
            _items_to_delete,
            _items_not_online,
        )

    def _get_checksum(
        self,
        content,
    ):
        """get Check sum of the content

        Args:
            content (_type_): content to get checksum

        Returns:
            _type_: returns the checksum
        """
        _md5_hash = hashlib.md5()
        _data = content.encode(encoding="utf-8")
        _md5_hash.update(_data)
        _checksum = _md5_hash.digest()
        _checksum_base64 = base64.b64encode(_checksum)
        _base64_str = _checksum_base64.decode("utf-8")
        return _base64_str

    def process_item_to_delete(
        self,
        item_to_delete: Document,
        op: str,
    ):
        """process item to delete

        Args:
            item_to_delete (Document): item to delete

        Raises:
            CustomException: custom exception
        """
        _id = None
        _result = None
        try:
            st = time.time()

            _index_name = self._index_name
            _id = item_to_delete.id

            _search_manager = self._search_manager

            # remove documents from index
            _response = _search_manager.remove_content(
                _index_name,
                _id,
            )
            if _response == 0:
                logging.info(
                    "Document id : %s not found in the index",
                    _id,
                )
            _document_manager = DocumentManager()
            _document_manager.retire(item_to_delete)

            et = time.time()
            logging.info(
                "Time taken to delete article %s is %s",
                _id,
                et - st,
            )
            _result = {
                "id": _id,
                "status": "Success",
            }
        except Exception as e:
            _result = {
                "id": _id,
                "status": "Failed",
                "error": e,
            }
        return _result

    def _run(
        self,
        _items,
        _function,
        _op,
    ):
        for _i in range(0, len(_items), MAX_ITEMS):
            _sub_items = _items[_i : _i + MAX_ITEMS]
            st = time.time()
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=MAX_WORKERS,
            ) as executor:
                # Start the load operations and mark each future with its URL
                _future = {
                    executor.submit(_function, _item, _op): _item
                    for _item in _sub_items  # noqa: E501
                }  # noqa: E501
                for future in concurrent.futures.as_completed(_future):
                    _result = future.result()
                    if _result["status"] == "Failed":
                        logging.error(
                            "Failed to %s article %s",
                            _op,
                            _result["id"],
                            exc_info=_result["error"],
                        )
            et = time.time()
            logging.info(
                "Time taken to %s %s articles is %s seconds",
                _op,
                len(_sub_items),
                et - st,
            )
            logging.info(
                "Completed %s out of %s articles",
                _i + MAX_ITEMS,
                len(_items),
            )

    def run(self):
        """Run the super search process."""
        _build_id = os.getenv("BUILD_ID", "Local Build")
        logging.info(
            "Running super search for build id %s",
            _build_id,
        )
        _speed_perform_list = self.get_speed_perform_list()
        logging.info(
            "Got %s articles from speed perform api.", len(_speed_perform_list)
        )

        _metadata_list = self.get_metadata_list()
        logging.info("Got %s documents from metadata.", len(_metadata_list))

        (
            _items_to_add,
            _items_to_update,
            _items_to_delete,
            _items_not_online,
        ) = self.get_delta(
            _speed_perform_list,
            _metadata_list,
        )

        logging.info("%s articles to add", len(_items_to_add))
        logging.info("%s articles to update", len(_items_to_update))
        logging.info("%s articles to delete", len(_items_to_delete))
        logging.info("%s articles not online", len(_items_not_online))

        self._run(
            _items_to_add,
            self.index_article,
            "add",
        )

        self._run(
            _items_to_update,
            self.index_article,
            "update",
        )

        self._run(
            _items_to_delete,
            self.process_item_to_delete,
            "delete",
        )
