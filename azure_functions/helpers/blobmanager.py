"This module contains the class for handling all operations related to BLOB."
import json
import hashlib
import base64

from azure.storage.blob import BlobServiceClient


class BlobManager:
    "class for handling all operations related to BLOB"

    def get_blob_content(
        self, container_path, base_path, accountcredentials, container_url
    ):
        "to get the Blob content related to file path provided"
        blob_service_client = BlobServiceClient(
            account_url=base_path, credential=accountcredentials
        )
        # Get the blob client for the specified file
        blob_client = blob_service_client.get_blob_client(
            container=container_url, blob=container_path
        )
        blob_data = blob_client.download_blob()
        # Download the content of the file
        blob_content = blob_data.readall()
        return blob_content

    def get_json_content(
        self, container_path, base_path, accountcredentials, container_url
    ):
        "to get the Blob content related to file path provided"
        blob_service_client = BlobServiceClient(
            account_url=base_path, credential=accountcredentials
        )
        # Retrieve files from ADLS container
        # Read blob content
        # Get the blob client for the specified file
        blob_client = blob_service_client.get_blob_client(
            container=container_url, blob=container_path
        )
        blob_data = blob_client.download_blob().content_as_text()
        # Download the content of the file
        json_data = json.loads(blob_data)
        return json_data

    # uploading the blob in the container
    def get_checksum(self, data):
        "to get the Blob content related to file path provided"
        md5_hash = hashlib.md5()
        md5_hash.update(data)
        checksum = md5_hash.digest()

        # Convert the checksum to base64 encoding
        checksum_base64 = base64.b64encode(checksum)
        return checksum_base64
