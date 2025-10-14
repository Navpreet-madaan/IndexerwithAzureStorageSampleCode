"""
This class is a connector to integrate with the Speedperform API.
"""

import os
import requests

from common.handlers import KeyVaultHandler
from supersearch.articleinfo import ArticleJSONDecoder

TIMEOUT: int = 30


class DuplicateError(Exception):
    """
    This class is a custom exception for duplicate errors.
    """

    pass


class SpeedPerformAPI:
    """
    This class is a connector to integrate with the Speedperform API.
    """

    def __init__(self) -> None:
        _key_vault_handler = KeyVaultHandler()

        self._url = _key_vault_handler.get_secret(
            secret_name="speedperform-api-endpoint",
        )

        _api_token = _key_vault_handler.get_secret(
            secret_name="speedperform-api-token",
        )
        _client_id = _key_vault_handler.get_secret(
            secret_name="speedperform-client-id",
        )
        _channel_id = _key_vault_handler.get_secret(
            secret_name="speedperform-channel-id",
        )
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_api_token}",
            "ClientId": _client_id,
            "ChannelId": _channel_id,
        }

    def list(
        self,
    ):
        """
        Get a list of all article metadata
        """
        _url = self._url
        _headers = self._headers

        _response = requests.get(
            url=_url,
            headers=_headers,
            timeout=TIMEOUT,
        )
        _articles = _response.json(cls=ArticleJSONDecoder)
        self.check_for_duplicates(_articles)
        return _articles

    def get(
        self,
        article_id,
    ):
        """
        Get the details of an article
        """
        _url = self._url
        _headers = self._headers
        _article_id = article_id

        _url = f"{_url}/{_article_id}"
        _response = requests.get(
            url=_url,
            headers=_headers,
            timeout=TIMEOUT,
        )
        return _response.text, _url

    def check_for_duplicates(
        self,
        articles,
    ):
        """
        Get the details of an article
        """
        _articles = articles

        # Get the ids of the articles in a list
        _article_ids = [article.id for article in _articles]

        # Check for duplicates in the list

        _duplicates = list(set([x for x in _article_ids if _article_ids.count(x) > 1]))

        if len(_duplicates) > 0:
            _build_id = os.getenv("BUILD_ID", "Local Build")
            raise DuplicateError(
                f"Duplicates found for super search for build id {_build_id}. List of duplicates: {str(_duplicates)}"
            )
