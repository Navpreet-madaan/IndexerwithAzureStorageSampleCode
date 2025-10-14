"""Super agent manager class used for all super agent related operations.
To build the knowledge base, the Super Agent Manager class
processes the JSON data to extract specific

    Raises:
        Exception: Exception is raised if no content is extracted
        from the provided document.
        Exception: Exception is raised if indexes are not created.

    Returns:
        _type_: return the results of the operation.
"""

import json
from dataclasses import dataclass
from datetime import datetime

from superagent.blob import BlobHandler
from superagent.config import (
    ConfigurationHandler,
    SuperAgentConfig,
)
from superagent.summary import Summary


@dataclass
class SuperAgentManager:
    """Manager for ingesting data."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the Manger class."""

        _config_name = kwargs.get("config_name")
        self._logger = kwargs.get("logger")

        self.local_download_folder = None

        _configuration = ConfigurationHandler().load(_config_name)

        self.config_name = _config_name
        self.configuration = _configuration

        self._initalize_documents_store()

      
        self.superagent_summary: Summary = Summary(config_name=self.config_name)

    def _initalize_documents_store(
        self
    ):
        _configuration: SuperAgentConfig = self.configuration

        self.documents_storage_account_url = _configuration.documents.storage.account
        self.documents_container_name = _configuration.documents.storage.container

        BlobHandler.ensure_container_exists(
            storage_account_url=self.documents_storage_account_url,
            container_name=self.documents_container_name,
        )
        self._logger.info(
            "Documents storage account url: %s",
            self.documents_storage_account_url,
        )
        self._logger.info(
            "Documents container name: %s",
            self.documents_container_name,
        )

    def save_summary(
        self,
        run_start_time: datetime,
        container: str = None,
    ):
        """save crawl summary

        Args:
            summary (_type_): summary

        Raises:
            Exception: exception in case of failure

        Returns:
            _type_: response
        """
        if self.configuration.logs:
            _logs_storage_account_url = self.configuration.logs.storage.account
            _logs_container_name = self.configuration.logs.storage.container
            _file_name = container.split("/")[-1] if container else "no_blob_found"
            _file_name = (
                _file_name.replace(".json", "") if ".json" in _file_name else _file_name
            )
            _build_id = self.superagent_summary.build_id
            _config_name = (
                self.superagent_summary.config_name.replace(".yaml", "")
                if ".yaml" in self.superagent_summary.config_name
                else self.superagent_summary.config_name
            )

            _log_time = run_start_time.strftime("%Y%m%d/%H%M%S")
            _file_name = f"{_file_name}_log_summary.json"
            _blob_path = f"{_log_time}/{_build_id}/{_config_name}/{_file_name}"
            self.superagent_summary.log = _blob_path

            BlobHandler.ensure_container_exists(
                storage_account_url=_logs_storage_account_url,
                container_name=_logs_container_name,
            )

            _superagent_summary_content = json.dumps(
                self.superagent_summary.get_full_log(),
                indent=4,
            )
            BlobHandler.upload(
                storage_account_url=_logs_storage_account_url,
                container_name=_logs_container_name,
                blob_path=f"{self.configuration.logs.storage.path}/{_blob_path}",
                content=_superagent_summary_content,
                overwrite=True,
            )
        return self.superagent_summary.get_metrics()
