"""Configuration used within the solution"""

import os
import argparse
import yaml

from typing import List, Optional
from pydantic import BaseModel

from azure.identity import AzureCliCredential

from superagent.blob import BlobHandler


class Storage(BaseModel):
    account: str
    container: str
    path: str

class OpenAI(BaseModel):
    endpoint: str
    modeldeployment: str
    version: str
    temperature: float
    IndexName: str
    searchendpoint: str
    questionmodeldeployment: str
    questionmodelversion: str
    wordlimit:int


class Document(BaseModel):
    storage: Optional[Storage] = None


class Logs(BaseModel):
    storage: Storage


class SuperAgentIndex(BaseModel):
    storage: Storage
    
    
class StorageOutput(BaseModel):
    storage: Storage
    

class SuperAgentConfig(BaseModel):
    documents: Document
    storageoutput:Optional[StorageOutput] = None
    logs: Optional[Logs] = None
    index: Optional[SuperAgentIndex] = None    
    openai: Optional[OpenAI] = None


# Configuration used within the solution
class ConfigurationHandler:
    """Configuration used within the solution"""

    def __init__(
        self,
        args=None,
        credential=None,
    ):
        _storage_account_url = None
        _container_name = None
        _folder_name = None
        self.args = args
        self.credential = credential
        if args:
            _storage_account_url = args.storage_account_url
            _container_name = args.container_name
            _folder_name = args.folder_name
        else:

            _storage_account_url = os.getenv(
                "DOWNLOAD_CONFIGURATION_STORAGE_ACCOUNT_URL",
                None,
            )
            if not _storage_account_url:
                raise ValueError(
                    "Storage account url not provided in the environment variable DOWNLOAD_CONFIGURATION_STORAGE_ACCOUNT_URL"
                )

            _container_name = os.getenv(
                "DOWNLOAD_CONFIGURATION_CONTAINER_NAME",
                None,
            )
            _folder_name = os.getenv(
                "DOWNLOAD_CONFIGURATION_FOLDER_NAME",
                None,
            )
            if not _container_name:
                raise ValueError(
                    "Container name not provided in the environment variable DOWNLOAD_CONFIGURATION_CONTAINER_NAME"
                )

        self.configuration_storage_account_url = _storage_account_url
        self.configuration_container_name = _container_name
        self.configuration_folder_name = _folder_name

        BlobHandler.ensure_container_exists(
            storage_account_url=self.configuration_storage_account_url,
            container_name=self.configuration_container_name,
            credential=self.credential,
        )

    def exists(
        self,
        config_name,
    ):
        return BlobHandler.blob_exists(
            storage_account_url=self.configuration_storage_account_url,
            container_name=self.configuration_container_name,
            blob_path=f"{self.configuration_folder_name}/{config_name}",
        )

    def get_config_names(
        self,
        config_name,
    ):
        """Get configuration names and schedules.

        Returns:
            list: List of with their configurations and schedules.
        """
        _configuration = BlobHandler.download(
            storage_account_url=self.configuration_storage_account_url,
            container_name=self.configuration_container_name,
            blob_path=f"{self.configuration_folder_name}/{config_name}",
        )
        _configuration = yaml.safe_load(_configuration)
        # Preprocess raw into the expected dictionary format
        _raw_config = _configuration.get("superagent", [])
        return _raw_config

    def delete_urls(self, file_name):
        """Clear URLs from the specified YAML file after processing."""
        # Download the current configuration from the Blob storage
        _configuration = BlobHandler.download(
            storage_account_url=self.configuration_storage_account_url,
            container_name=self.configuration_container_name,
            blob_path=f"{self.configuration_folder_name}/{file_name}",
        )

        # Load the configuration and parse it as YAML
        _configuration = yaml.safe_load(_configuration)

        # Modify the content (in this case, clearing the URLs)

        # Upload the modified configuration back to the Blob storage
        BlobHandler.upload(
            storage_account_url=self.configuration_storage_account_url,
            container_name=self.configuration_container_name,
            blob_path=f"{self.configuration_folder_name}/{file_name}",
            content=yaml.dump(_configuration),  # Convert the dict back to
            overwrite=True,
        )

    def load(
        self,
        name: str,
    ):
        """Load configuration

        Args:
            name (str): configuration name

        Returns:
            object: configuration
        """
        _configuration = BlobHandler.download(
            storage_account_url=self.configuration_storage_account_url,
            container_name=self.configuration_container_name,
            blob_path=f"{self.configuration_folder_name}/{name}"
        )
        _configuration = yaml.safe_load(_configuration)
        _validated_configuration = SuperAgentConfig.model_validate(
            _configuration["superagent"]
        )
        return _validated_configuration

    def save(
        self,
        name: str,
        configuration: object,
    ):
        """Save configuration
        This is only meant to be used for loading the configuration
        from a local file to the storage account.
        It is NOT meant to be used for saving configuration from
        the solution to the storage account.

        Args:
            name (str): configuration name
            configuration (object): configuration

        Raises:
            Exception: exception in case of failure
        """

        _configuration = yaml.dump(configuration)
        _configuration = _configuration.encode("utf-8")
        BlobHandler.upload(
            storage_account_url=self.configuration_storage_account_url,
            container_name=self.configuration_container_name,
            blob_path=f"{self.configuration_folder_name}/{name}",
            content=_configuration,
            overwrite=True,
            credential=self.credential,
        )

    def _load_local(self, name: str):
        """Load configuration from local file
        This is used to load the configuration from a local file
        before uploading it to the storage account.
        """
        with open(name, "r", encoding="utf-8") as file:
            _configuration = yaml.safe_load(file)
            return _configuration

    def upload(
        self,
        file_path: str,
    ):
        """Upload configuration to storage account


        Args:
            name (str): configuration name

        Raises:
            Exception: exception in case of failure
        """
        _configuration = self._load_local(name=file_path)
        if self.args.validate_only:
            SuperAgentConfig.model_validate(_configuration["superagent"])
        else:
            if not self.args.no_validate:
                SuperAgentConfig.model_validate(_configuration["superagent"])
            _blob_path = os.path.basename(file_path)
            _blob_path = f"{self.configuration_folder_name}/{_blob_path}"
            self.save(
                name=_blob_path,
                configuration=_configuration,
            )

    def remove_config(
        self,
        config_name: str,
    ):
        """Remove a configuration"""
        BlobHandler.delete(
            storage_account_url=self.configuration_storage_account_url,
            container_name=self.configuration_container_name,
            blob_path=f"{self.configuration_folder_name}/{config_name}",
        )

    def load_local(self, file_path: str):
        _configuration = self._load_local(name=file_path)
        return SuperAgentConfig.model_validate(_configuration["superagent"])


def main():
    parser = argparse.ArgumentParser(description="Configuration")
    parser.add_argument(
        "--storage-account-url",
        type=str,
        help="Storage account url",
        required=True,
    )
    parser.add_argument(
        "--container-name",
        type=str,
        help="Container name",
        required=True,
    )
    parser.add_argument(
        "--folder-name",
        type=str,
        help="Folder name",
        required=True,
    )
    parser.add_argument(
        "--file-path",
        type=str,
        help="File path",
        required=True,
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="File path",
        required=False,
        default=False,
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="File path",
        required=False,
        default=False,
    )
    args = parser.parse_args()

    _configuration = ConfigurationHandler(
        args,
        credential=AzureCliCredential(),
    )
    _configuration.upload(
        file_path=args.file_path,
    )


if __name__ == "__main__":
    main()
