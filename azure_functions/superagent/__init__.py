"""
Supersearch processing module
"""
import os
import json
import logging

from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from superagent.config import ConfigurationHandler
from superagent.manager import SuperAgentManager
from superagent.ingest import Ingester


class SuperAgent:
    """
    This class handles the logic for creating an index for Super Agent.
    """
    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        """Initialize the WebCrawler class"""

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(
            os.environ.get(
                "SUPERAGENT_LOG_LEVEL",
                "INFO",
            )
        )
        self._credential = DefaultAzureCredential()

    def exists(
        self,
        *args,
        **kwargs,
    ):
        _config_name = kwargs.get("config_name", None)
        return ConfigurationHandler().exists(
            config_name=_config_name,
        )

    def extract(
        self,
        *args,
        **kwargs,
    ):        
        _config_name = kwargs.get("config_name", None)
        if self.exists(
            config_name=_config_name,
        ):
            _config_names = ConfigurationHandler().get_config_names(config_name=_config_name)
            _run_start_time = datetime.utcnow()
            for _config in _config_names:
                self._process(
                    config_name=_config,
                    run_start_time=_run_start_time,
                )

    def _process(
        self,
        config_name: str,
        run_start_time: datetime,
    ):
        """Run the superagent"""
        _build_id = os.getenv("BUILD_ID", "Local Build")
        _config_name = config_name

        # Run superagent in the same process
        _return_dict = {}
        self._run_process(_config_name, run_start_time, _return_dict)
        _superagent_summary = _return_dict["superagent_summary"]
        self._logger.info(
            json.dumps(_superagent_summary),
        )
        self._logger.info(
            "Crawl completed for build id %s for %s",
            _build_id,
            config_name,
        )

    def _run_process(
        self,
        config_name: str,
        run_start_time: datetime,
        return_dict: dict,
    ):

        _superagent_manager = SuperAgentManager(
            config_name=config_name,
            logger=self._logger)
        _configuration = _superagent_manager.configuration

        _ingester = Ingester(
            superagent_manager=_superagent_manager,
            configuration=_configuration,
            credential=self._credential,
            superagent_summary=_superagent_manager.superagent_summary,
            logger=self._logger,
            config_name=config_name,
        )
        return_dict["superagent_summary"] = []
        conatiner_path = _ingester.data_exists()
        if conatiner_path:
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_container = {
                    executor.submit(_ingester.ingest_page, container): container
                    for container in conatiner_path
                }

                for future in as_completed(future_to_container):
                    container = future_to_container[future]
                    try:
                        result = future.result()
                        if result:
                            _superagent_manager.superagent_summary.end_time = datetime.now(timezone.utc)
                            return_dict["superagent_summary"].append(
                                _superagent_manager.save_summary(
                                    run_start_time=run_start_time, container=container
                                )
                            )
                    except Exception as e:
                        self._logger.error(f"Failed to ingest {container}: {e}")
        else:
            self._logger.info("No data to ingest for %s", config_name)
            _superagent_manager.superagent_summary.end_time = datetime.now(timezone.utc)
            return_dict["superagent_summary"].append(
                _superagent_manager.save_summary(
                    run_start_time=run_start_time, container=None
                )
            )
        # if len(conatiner_path) > 0:
        #     for container in conatiner_path:
        #         result = _ingester.ingest_page(container)
        #         if result:
        #             _superagent_manager.superagent_summary.end_time = datetime.now(
        #                 timezone.utc
        #             )
        #             return_dict["superagent_summary"].append(
        #                 _superagent_manager.save_summary(
        #                     run_start_time=run_start_time, container=container
        #                 )
        #             )                
        # else:
        #     self._logger.info(
        #         "No data to ingest for %s",
        #         config_name,
        #     )
        #     _superagent_manager.superagent_summary.end_time = datetime.now(timezone.utc)
        #     return_dict["superagent_summary"].append(
        #         _superagent_manager.save_summary(
        #             run_start_time=run_start_time, container=None
        #         )
        #     )
