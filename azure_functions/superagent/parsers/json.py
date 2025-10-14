"""JSON Parser for agent."""

import re
import os
import json
import base64
from typing import List
from bs4 import BeautifulSoup
from langchain.text_splitter import MarkdownTextSplitter
from superagent.qgen import QuestionGenerator
from superagent.config import SuperAgentConfig


class JSONParser:
    """
    ASPX parser for the superagent.
    """

    def __init__(self, *args, **kwargs):
        self.configuration: SuperAgentConfig = kwargs.get("configuration")
        self.superagent_summary = kwargs.get("summary")
        self._logger = kwargs.get("logger")

    @classmethod
    def read_json(cls, *args, **kwargs):
        """
        Store the JSON content in Azure Blob Storage.
        """
        # Store the content in Azure Blob Storage
        _superagent_manager = kwargs.get("superagent_manager")
        _response = kwargs.get("response")
        _logger = kwargs.get("logger")
        _blob_path = kwargs.get("blob_path")
        _container = kwargs.get("container")
        _json_parser = JSONParser(
            configuration=_superagent_manager.configuration,
            summary=_superagent_manager.superagent_summary,
            logger=_logger,
        )
        _contents = _json_parser.extract_metadata(_response, _blob_path, _container)
        if _contents:
            return _contents
        else:
            _logger.error("No content extracted from JSON file.")
            return None
        
    def extract_metadata(self, json_content: bytes, blob_path: str, container: str):
        """
        Cleans the JSON content by removing extra whitespace and special characters.

        Returns:
            A list of dictionaries, where each dictionary contains the content
            and metadata for the page. Metadata must comply with HTTP header rules,
            and the content must be a byte array encoded in UTF-8.
        """
        # Extract fields
        data = json.loads(json_content.decode("utf-8"))
        page_title = data.get("Title", "No Title Found")
        page_description = data.get("ARM_ProductDetail_Description", "No Description Found")
        parent_path = data.get("ARM_Content_Reference", "No Parent Found")
        html_content = data.get("ARM_Content_IndexData", "")
        # If HTML is empty, fallback to the full JSON as a string
        if not html_content:
            html_content = json.dumps(data)
        # Clean and parse content HTML
        soup = BeautifulSoup(html_content, "html.parser")
        page_text = re.sub(r"[\n\r\t]", "", soup.get_text()).strip()

        # Chunk the content
        _chunks = self.custom_markdown_chunking(html_content) if html_content else []
        fullpath = os.environ.get("SharePointURL") + parent_path        
        # Encode metadata
        encoded_metadata = {
            "title": base64.b64encode(page_title.encode("utf-8")).decode("utf-8"),
            "description": base64.b64encode(page_description.encode("utf-8")).decode("utf-8"),
            "parent_id": base64.b64encode(parent_path.encode("utf-8")).decode("utf-8"),
            "blob_path": base64.b64encode(blob_path.encode("utf-8")).decode("utf-8"),
            "source_address": base64.b64encode(fullpath.encode("utf-8")).decode("utf-8"),
        }

        # Generate question for each chunk if present
        if _chunks:
            # _question_generator = QuestionGenerator(
            #     open_ai_endpoint=self.configuration.openai.endpoint,
            #     open_ai_api_version=self.configuration.openai.questionmodelversion,
            #     open_ai_deployment_name=self.configuration.openai.questionmodeldeployment,
            #     temperature=self.configuration.openai.temperature,
            # )

            return [
                {
                    "content": chunk.encode("utf-8"),
                    "metadata": {
                        **encoded_metadata,
                        "generatedquestion": "",
                    },
                }
                for chunk in _chunks
            ]

        return None

    def custom_markdown_chunking(self, content: str) -> List[str]:
        """
        Split content using MarkdownTextSplitter from LangChain.
        Fallback to simple line-based splitting if unavailable.
        """
        try:
            from langchain.text_splitter import MarkdownTextSplitter
            splitter = MarkdownTextSplitter()
            return splitter.split_text(content)
        except ImportError:
            # Fallback method if LangChain isn't available
            return [content[i:i+1000] for i in range(0, len(content), 1000)]
