from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


class BlobHandler:

    @classmethod
    def upload(
        cls,
        storage_account_url: str,
        container_name: str,
        blob_path: str,
        content: bytes,
        metadata: dict = None,
        overwrite: bool = False,
        credential=None,
    ):
        """Upload blob

        Args:
            storage_account_url (_type_): storage account url
            container_name (_type_): container name
            blob_path (_type_): blob path
            content (_type_): content
            metadata (_type_): metadata
            overwrite (_type_): overwrite

        Raises:
            Exception: exception in case of failure

        Returns:
            None
        """
        _credential = DefaultAzureCredential()
        if credential:
            _credential = credential
        _blob_service_client = BlobServiceClient(
            account_url=storage_account_url,
            credential=_credential,
        )
        _container_client = _blob_service_client.get_container_client(
            container=container_name
        )

        _blob_client = _container_client.upload_blob(
            name=blob_path,
            data=content,
            overwrite=overwrite,
            metadata=metadata,
        )

    @classmethod
    def download(
        cls,
        storage_account_url: str,
        container_name: str,
        blob_path: str,
        credential=None,
    ):
        """Download blob

        Args:
            storage_account_url (_type_): storage account url
            container_name (_type_): container name
            blob_path (_type_): blob path

        Raises:
            Exception: exception in case of failure

        Returns:
            _type_: response
        """
        _credential = DefaultAzureCredential()
        if credential:
            _credential = credential

        _blob_service_client = BlobServiceClient(
            account_url=storage_account_url,
            credential=_credential,
        )
        _container_client = _blob_service_client.get_container_client(
            container=container_name
        )
        _blob_client = _container_client.get_blob_client(blob=blob_path)
        _blob = _blob_client.download_blob().readall()
        return _blob

    @classmethod
    def ensure_container_exists(
        cls,
        storage_account_url: str,
        container_name: str,
        credential=None,
    ):
        """Ensure container exists

        Args:
            storage_account_url (_type_): storage account url
            container_name (_type_): container name
            credential (_type_): credential
        Raises:
            Exception: exception in case of failure

        Returns:
            _type_: response
        """
        _credential = DefaultAzureCredential()
        if credential:
            _credential = credential
        _blob_service_client = BlobServiceClient(
            account_url=storage_account_url,
            credential=_credential,
        )
        _container_client = _blob_service_client.get_container_client(
            container=container_name
        )
        if not _container_client.exists():
            _container_client.create_container()

    @classmethod
    def get_properties(
        cls,
        storage_account_url: str,
        container_name: str,
        blob_path: str,
    ):
        """Get properties

        Args:
            storage_account_url (_type_): storage account url
            container_name (_type_): container name
            blob_path (_type_): blob path

        Raises:
            Exception: exception in case of failure

        Returns:
            _type_: response
        """
        _credential = DefaultAzureCredential()

        _blob_service_client = BlobServiceClient(
            account_url=storage_account_url,
            credential=_credential,
        )
        _container_client = _blob_service_client.get_container_client(
            container=container_name
        )
        _blob_client = _container_client.get_blob_client(blob=blob_path)
        _properties = _blob_client.get_blob_properties()
        return _properties

    @classmethod
    def list(
        cls,
        storage_account_url: str,
        container_name: str,
        blob_path: str,
    ):
        """List blobs

        Args:
            blob_path (_type_): blob path

        Raises:
            Exception: exception in case of failure

        Returns:
            _type_: response
        """
        _credential = DefaultAzureCredential()

        _blob_service_client = BlobServiceClient(
            account_url=storage_account_url,
            credential=_credential,
        )
        _container_client = _blob_service_client.get_container_client(
            container=container_name
        )
        _blobs = _container_client.list_blobs(name_starts_with=blob_path)
        return _blobs

    @classmethod
    def delete(
        cls,
        storage_account_url: str,
        container_name: str,
        blob_path: str,
    ):
        """Delete blob

        Args:
            storage_account_url (_type_): storage account url
            container_name (_type_): container name
            blob_path (_type_): blob path

        Raises:
            Exception: exception in case of failure

        Returns:
            None
        """
        _credential = DefaultAzureCredential()

        _blob_service_client = BlobServiceClient(
            account_url=storage_account_url,
            credential=_credential,
        )
        _container_client = _blob_service_client.get_container_client(
            container=container_name
        )
        _blob_client = _container_client.get_blob_client(blob=blob_path)
        _blob_client.delete_blob()

    @classmethod
    def blob_exists(
        cls,
        storage_account_url: str,
        container_name: str,
        blob_path: str,
    ):
        """Check if blob exists

        Args:
            storage_account_url (_type_): storage account url
            container_name (_type_): container name
            blob_path (_type_): blob path

        Raises:
            Exception: exception in case of failure

        Returns:
            _type_: response
        """
        _credential = DefaultAzureCredential()

        _blob_service_client = BlobServiceClient(
            account_url=storage_account_url,
            credential=_credential,
        )
        _container_client = _blob_service_client.get_container_client(
            container=container_name
        )
        _blob_client = _container_client.get_blob_client(blob=blob_path)
        return _blob_client.exists()
    
    @classmethod
    def get_blob_list(
        cls, container_name, directory_path, accountcredentials, account_url
    ):
        """Get list of blobs under given path"""
        if not accountcredentials:
            accountcredentials = DefaultAzureCredential()

        # Connect to Azure Blob Storage
        blob_service_client = BlobServiceClient(
            account_url=account_url, credential=accountcredentials
        )

        # Get the container client for the specified container
        container_client = blob_service_client.get_container_client(container_name)

        # List all blobs under the given directory path
        blobs_list = container_client.list_blobs(name_starts_with=directory_path, include=["metadata"])
        blobs_info = []
        for blob in blobs_list:
            blobs_info.append({
            "name": blob.name,
            "size": blob.size,
            "last_modified": blob.last_modified})
        blobs_info.sort(key=lambda x: x["last_modified"])

        # Return only the blob names in sorted order
        #sorted_blob_names = [blob[0] for blob in blobs_info]
        return blobs_info

    @classmethod
    def get_Blob_Content(
        cls, container_path, base_path, accountcredentials, container_url
    ):
        """to get the Blob content related to file path provided"""
        if not accountcredentials:
            accountcredentials = DefaultAzureCredential()

        # Connect to Azure Data Lake Storage
        blob_service_client = BlobServiceClient(
            account_url=base_path, credential=accountcredentials
        )
        # Get the blob client for the specified file
        blob_client = blob_service_client.get_blob_client(
            container=container_url, blob=container_path
        )

        self.ensure_blob_exists(
            storage_account_url=base_path,
            container_name=container_url,
            blob_name=container_path,
            credential=None,
        )

        blob_data = blob_client.download_blob()
        # Download the content of the file
        blob_content = blob_data.readall()
        return blob_content