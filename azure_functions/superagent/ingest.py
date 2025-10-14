import os
import json
import uuid
import logging
import hashlib
import base64
import yaml
import re
import time
import numpy as np
from openai import AzureOpenAI, OpenAI
from azure.core.credentials import AccessToken
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential

from superagent.blob import BlobHandler
from superagent.config import SuperAgentConfig
from superagent.summary import Summary
from superagent.parsers.aspx import ASPXParser
from superagent.parsers.json import JSONParser


class Ingester:
    """Ingests data into the database."""

    def __init__(self, *args, **kwargs):
        self._logger = kwargs.get("logger")
        self.configuration: SuperAgentConfig = kwargs.get("configuration")
        self.credential = kwargs.get("credential")
        self.superagent_manager = kwargs.get("superagent_manager")
        self.superagent_summary = kwargs.get("superagent_summary")
        self.config_name = kwargs.get("config_name")
        self.token: Optional[AccessToken] = None
        self.open_ai_service = self.configuration.openai.endpoint
        self.open_ai_model_name = self.configuration.openai.modeldeployment
        # BlobHandler.ensure_container_exists(
        #     storage_account_url=self.configuration.index.storage.account,
        #     container_name=self.configuration.index.storage.container,
        #     credential=self.credential,
        # )

        self.container_path = []
        self.file_blob_path = []
        
    
    def data_exists(
        self,
    ):
        directory_path = self.configuration.documents.storage.path + "/"
        file_blobs = BlobHandler.get_blob_list(
            container_name=self.configuration.documents.storage.container,
            directory_path=directory_path,
            accountcredentials=self.credential,
            account_url=self.configuration.documents.storage.account,
        )
        if file_blobs:
            for blob in file_blobs:
                # Check if the blob has a non-zero size
                if blob["size"] and blob["size"] > 0:
                    containerPath = (
                        f"{self.configuration.documents.storage.container}/{blob['name']}"
                    )
                    self.container_path.append(containerPath)
                    _, file_blob_path = containerPath.split("/", 1)
                    self.file_blob_path.append(file_blob_path)
            return self.container_path
        else:
            return self.container_path
  
    
    def ingest_page(self, container):
        """Ingesting page into the  Storage account."""

        self._container = container
        logging.info(f"Ingesting blob: {self._container}")
        _new_pages = []
        _updated_pages = []
        _deleted_pages = []
        _unchanged_pages = []
        _summary_pages = {}
        container_name, file_blob_path = self._container.split("/", 1)
        # Get the filename without the directory path
        file_name = os.path.basename(self._container)
        # Remove the file extension
        file_name_without_ext, file_ext = os.path.splitext(file_name)
        # Only process JSON files for now
        # if file_ext.lower() != ".json" or file_ext.lower() != ".aspx":
        #     logging.info(f"Skipping non file: {file_name}")
        #     return False
        blob_content = BlobHandler.download(
            self.configuration.documents.storage.account,
            container_name,
            file_blob_path,
            self.credential,
        )
        if not blob_content:
            logging.error("Error: Blob content is empty")
            return False
        # Decode the blob content
        # File type to parser method mapping
        parser_map = {
            ".aspx": ASPXParser.read_aspx,
            ".json": JSONParser.read_json
        }
        
        parser_func = parser_map.get(file_ext.lower())
        
        # Read current index
        index_data = self._read_index()
        checksum = self._get_checksum(blob_content.decode("utf-8"))
        if file_blob_path in index_data:
            # prevchecksum = index_data[file_blob_path]
            state = "unchanged"
            # blob_content = BlobHandler.delete(
            #     self.configuration.documents.storage.account,
            #     container_name,
            #     file_blob_path)
            # state = self._compare(checksum, prevchecksum)
        else:
            # New entry: add to index and upload
            index_data[file_blob_path] = checksum
            self._save_index(index_data)
            state = "new"
            # Dynamically invoke the parser method
            _chunks = parser_func(
                superagent_manager=self.superagent_manager,
                response=blob_content,
                logger=self._logger,
                blob_path=file_blob_path,
                container=self._container            
            )
            for i, _chunk in enumerate(_chunks):
                self._store_pages(
                    _chunk["content"],  # Extract content,
                    _chunk["metadata"], # Extract metadata
                    file_name_without_ext,
                    index=i)                   
        # if state:
        #     for _chunk in _chunks:
        #         if state.lower() == "new":
        #             _new_pages.append(_chunk)
        #         if state.lower() == "unchanged":
        #             _unchanged_pages.append(_chunk)
        #         if state.lower() == "updated":
        #             _updated_pages.append(_chunk)

        #     if _new_pages:
        #         for _page_data in _new_pages:
        #             self._store_pages(
        #                 _page_data["content"],  # Extract content,
        #                 _page_data["metadata"], # Extract metadata
        #                 file_name_without_ext,
        #             )

        #     if _updated_pages:
        #         for _page_data in _updated_pages:
        #             self._store_pages(
        #                 _page_data["content"],  # Extract content,
        #                 _page_data["metadata"], # Extract metadata
        #                 file_name_without_ext,
        #             )
                    
        # # update superagent summary logs
        # self.superagent_summary.new_file = [
        #     base64.b64decode(_a_page["metadata"]["title"]).decode("utf-8") for _a_page in _new_pages
        # ]
        # self.superagent_summary.updated_file = [
        #    base64.b64decode(_a_page["metadata"]["title"]).decode("utf-8") for _a_page in _updated_pages
        # ]
        # self.superagent_summary.unchanged_file = [
        #     base64.b64decode(_a_page["metadata"]["title"]).decode("utf-8") for _a_page in _unchanged_pages
        # ]
        return True
    
    
    def _get_checksum(
        self,
        content,
    ):
        _md5_hash = hashlib.md5()
        _data = content.encode(encoding="utf-8")
        _md5_hash.update(_data)
        _checksum = _md5_hash.digest()
        _checksum_base64 = base64.b64encode(_checksum)
        _base64_str = _checksum_base64.decode("utf-8")
        return _base64_str

    def _compare(self, checksum, prevchecksum):
        return "new" if not prevchecksum else "unchanged" if checksum == prevchecksum else "updated"
    
    def _read_index(
        self
    ):
        _credential = self.credential
        if BlobHandler.blob_exists(
            storage_account_url=self.configuration.index.storage.account,
            container_name=self.configuration.index.storage.container,
            blob_path=f"{self.configuration.index.storage.path}/{self.config_name}"
        ):
            blob_content = BlobHandler.download(
                storage_account_url=self.configuration.index.storage.account,
                container_name=self.configuration.index.storage.container,
                blob_path=f"{self.configuration.index.storage.path}/{self.config_name}"
            )
            if not blob_content:  # Handle empty content
                logging.info("Warning: No Index Summary found.")
                return {}
            _index = yaml.safe_load(blob_content.decode("utf-8"))
            return _index
        else:
            logging.info("Warning: No Index Summary found.")
            return {}

    def _save_index(
        self,
        pages,
    ):
        _credential = self.credential
        _index = yaml.dump(
            pages,
            indent=4,
        )
        _blob = BlobHandler.upload(
            storage_account_url=self.configuration.index.storage.account,
            container_name=self.configuration.index.storage.container,
            blob_path=f"{self.configuration.index.storage.path}/{self.config_name}",
            content=_index.encode("utf-8"),
            credential=_credential,
            overwrite=True,
        )
        # blob_content = BlobHandler.download(
        #         storage_account_url=self.configuration.index.storage.account,
        #         container_name=self.configuration.index.storage.container,
        #         blob_path=f"{self.configuration.index.storage.path}/{self.config_name}"
        # )
        # if not blob_content:  # Handle empty content
        #     logging.info("Warning: No Index Summary found.")
        #     return {}
        # _index = yaml.safe_load(blob_content.decode("utf-8"))
        # return _index

    def _store_pages(
        self,
        body: dict,
        metadata: dict,
        blob_path: str,
        index: int = 0  # Add index to uniquely identify chunks
    ):
        _credential = self.credential
        decoded_body = body.decode("utf-8")
        
        # Remove ASPX tags and clean the content
        cleaned_body = re.sub(r"<.*?>", "", decoded_body).strip()
        json_content = {
            "content": cleaned_body
            }
        # Serialize the JSON content
        json_body = json.dumps(json_content, indent=4)
        # Append index to blob path for unique file names: filename_0.json, filename_1.json, ...
        full_blob_path = f"{blob_path}_{index}.json"
        BlobHandler.upload(
            storage_account_url=self.configuration.storageoutput.storage.account,
            container_name=self.configuration.storageoutput.storage.container,
            blob_path=f"{self.configuration.storageoutput.storage.path}/{full_blob_path}",
            content=json_body,
            metadata=metadata,
            credential=_credential,
            overwrite=True,
        )
        # _embeddings= self.generate_embedding(
        #     content=cleaned_body,
        # )
        # self.upload_index(_embeddings, cleaned_body, metadata)
        
    def generate_embedding(self, content):
        """Generate emeddings

        Args:
            content (content type): content for which emeddings to be generated
        Returns:
            _type_: return response in boolean for the success or failure
        """
        word_limit = self.configuration.openai.wordlimit  # Set the word limit for chunking
        if content: 
            _content = content
            # Split content into words
            words = content.split()
            
            # Create chunks of up to word_limit words
            chunks = [
                ' '.join(words[i:i + word_limit])
                for i in range(0, len(words), word_limit)
            ]
        # Initialize the Azure OpenAI client
        client = AzureOpenAI(
            azure_endpoint=self.open_ai_service,  # Azure OpenAI endpoint
            azure_deployment=self.open_ai_model_name,  # Deployment name (e.g., "text-embedding-ada-002")
            api_version=self.configuration.openai.version,  # API version (e.g., "2023-05-15")
            api_key=self.wrap_credential(),  # Pass the token,
        )
        embeddings = []  # Initialize the list before the loop
        for chunk in chunks:
            response = client.embeddings.create(
                input=chunk,
                model=self.open_ai_model_name
                )
            embeddings.append(response.data[0].embedding)
        # Convert embeddings to a list
        # ✅ Average the list of embeddings to get a single flat vector
        averaged_embedding = np.mean(embeddings, axis=0).tolist()

        return averaged_embedding
    
    def upload_index(self, embeddings, content, metadata):
        """Index Creation method

        Args:
            embeddings (_type_): embeddings
            content (_type_):  content
            metadata (_type_): metadata

        Raises:
            Exception: return exception in case of failure

        Returns:
            _type_: return the response in boolean for the success or failure
        """
        
        index_name = self.configuration.openai.IndexName       
        _response = False
        search_client = SearchClient(
            endpoint=self.configuration.openai.searchendpoint,
            index_name=index_name,
            credential=AzureKeyCredential(os.environ.get("SEARCH_KEY"))
        )
        # Decode Base64 metadata values
        base64_metadata = {
            key: self.decode_base64(value) if isinstance(value, str) else value
            for key, value in metadata.items()
        }
        documents = [
            {
                "parent_id": base64_metadata["parent_id"],  # Parent ID for the document
                "title": base64_metadata["title"],  # Title for the document
                "description": base64_metadata["description"],  # Description of the document
                "generatedquestion": base64_metadata["generatedquestion"],  # generatedquestion of the document
                "blob_path": base64_metadata["blob_path"],  # Blob path for the document
                "source_address": base64_metadata["source_address"],  # Source address of the document
                "chunk": content,  # Content of the document
                "chunk_id": str(uuid.uuid4()),  # Unique ID for the document
                "vector": embeddings,  # Embeddings for the document
            }
        ]
        with search_client as client:
            _response = client.upload_documents(documents)
            return _response
        if _response:
            return True
        else:
            raise Exception("Failed to create index")
        
    def wrap_credential(self) -> str:
        """Retrieves an Azure AD token for authentication"""
        if not self.token or self.token.expires_on <= time.time():
            self.token = self.credential.get_token(
                "https://cognitiveservices.azure.com/.default"
            )
        return self.token.token  # Return the bearer token
    
    def decode_base64(self, value):
        """Try decoding Base64 once, and if it's still Base64, decode again."""
        try:
            decoded_once = base64.b64decode(value).decode("utf-8")
            # Check if the first decode still looks like Base64 (only contains valid Base64 characters)
            try:
                decoded_twice = base64.b64decode(decoded_once).decode("utf-8")
                return decoded_twice  # If this works, return fully decoded value
            except:
                return decoded_once  # If second decode fails, return first decoded result
        except:
            return value  # If it's not Base64 at all, return original value