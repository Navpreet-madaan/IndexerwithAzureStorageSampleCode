"""ASPX Parser for agent."""

import re
import os
import base64
from bs4 import BeautifulSoup
from langchain.text_splitter import MarkdownTextSplitter
from superagent.qgen import QuestionGenerator
from superagent.config import SuperAgentConfig


class ASPXParser:
    """
    ASPX parser for the superagent.
    """

    def __init__(self, *args, **kwargs):
        self.configuration: SuperAgentConfig = kwargs.get("configuration")
        self.superagent_summary = kwargs.get("summary")
        self._logger = kwargs.get("logger")

    @classmethod
    def read_aspx(cls, *args, **kwargs):
        """
        Store the ASPX content in Azure Blob Storage.
        """
        # Store the content in Azure Blob Storage
        _superagent_manager = kwargs.get("superagent_manager")
        _response = kwargs.get("response")
        _logger = kwargs.get("logger")
        _blob_path = kwargs.get("blob_path")
        _container = kwargs.get("container")
        _aspx_parser = ASPXParser(
            configuration=_superagent_manager.configuration,
            summary=_superagent_manager.superagent_summary,
            logger=_logger,
        )
        _contents = _aspx_parser.extract_metadata(_response, _blob_path, _container)
        if _contents:
            return _contents
        else:
            _logger.error("No content extracted from ASPX page.")
            return None
        
    def extract_metadata(self, content: bytes, blob_path: str, container: str):
        """
        Cleans the ASPX content by removing extra whitespace and special characters.

        Returns:
            A list of dictionaries, where each dictionary contains the content
            and metadata for the page. Metadata must comply with HTTP header rules,
            and the content must be a byte array encoded in UTF-8.
        """
        # Parse ASPX content
        soup = BeautifulSoup(content, "html.parser")
        
        # Extract Page Title
        _page_title = (
            soup.find("SharePointWebControls:FieldValue", {"FieldName": "Title"}) or 
            soup.title or 
            " ".join(h1.get_text(strip=True) for h1 in soup.find_all("h1")) or 
            "No Title Found"
        )
        _page_title = " ".join(str(_page_title).split()[:100])  # Limit to 200 words
        # Extract and limit Descriptions (first <p> under each section, max 200 words)
        _page_description = " ".join(p.get_text(strip=True) for p in soup.find_all("p"))
        _page_description = " ".join(_page_description.split()[:150])  # Limit to 200 words
        if not _page_description.strip():  # Default if no description is found
            _page_description = "No Description Found"
        # Extract Parent (Breadcrumbs)
        breadcrumbs = soup.find("SharePointWebControls:ListSiteMapPath")
        parent_text = breadcrumbs.text.strip() if breadcrumbs else "No Parent Found"
        if breadcrumbs is None:
            parent_text = " | ".join(f"{a.get_text(strip=True)}: {a['href']}" for a in soup.find_all("a", href=True))
        if not parent_text.strip():  # Default if no parent ID is found
            parent_text = "No Parent Found"
        parent_text = " ".join(parent_text.split()[:100])  # Limit to 200 words
        
        # Serialize the modified HTML back to a string
        _page_text = re.sub(r"[\n\r\t]", "", soup.get_text()).strip()

        # Encode metadata to base64
        _title = base64.b64encode(_page_title.encode("utf-8")).decode("utf-8")
        _description = base64.b64encode(_page_description.encode("utf-8")).decode(
            "utf-8"
        )
        _parent_id = base64.b64encode(parent_text.encode("utf-8")).decode(
            "utf-8"
        )
        
        fullpath = os.environ.get("SharePointURL") + container
        source_address = base64.b64encode(fullpath.encode("utf-8")).decode("utf-8")
        blob_path = base64.b64encode(blob_path.encode("utf-8")).decode("utf-8")
       
        # Perform chunking using the custom_markdown_chunking method
        _chunks = None
        if len(content) > 0:
            _chunks = self.custom_section_anchor_chunking(content)

        if _chunks:
            # _question_generator = QuestionGenerator(
            #     open_ai_endpoint=self.configuration.openai.endpoint,
            #     open_ai_api_version=self.configuration.openai.questionmodelversion,
            #     open_ai_deployment_name=self.configuration.openai.questionmodeldeployment,
            #     temperature=self.configuration.openai.temperature,
            # )

            # Generate metadata for each chunk using a list comprehension
            return [
                {
                    "content": chunk.encode("utf-8"),
                    "metadata": {
                        "title": _title,
                        "description": _description,
                        "generatedquestion": _description,
                        "parent_id": _parent_id,
                        "blob_path": blob_path,
                        "source_address": source_address,
                    },
                }
                for chunk in _chunks
            ]

        return None

    def custom_markdown_chunking(self, content):
        """
        Split content using MarkdownTextSplitter from LangChain.
        Falls back to size-based chunking if input isn't markdown-like.
        """
        # Process the contentindexdata HTML content
        soup = BeautifulSoup(content, "html.parser")
        plain_text = soup.get_text(
            separator="\n", strip=True
        )  # Extract plain text from HTML

        # Use MarkdownTextSplitter to split the plain text
        splitter = MarkdownTextSplitter()
        chunks = splitter.split_text(plain_text)  # Now, you are splitting plain text
        return chunks

    def custom_section_anchor_chunking(self, content):
        soup = BeautifulSoup(content, "html.parser")
        chunks = []

        # Step 1: Find all <a href="#..."> section anchors
        anchors = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if href.startswith("#") and len(href) > 1:
                anchors.add(href[1:])

        # Step 2: Extract content for each anchor section
        for anchor in anchors:
            # Match <h3> tag containing <a name="anchor">
            h3_tag = soup.find(lambda tag: tag.name == "h3" and tag.find("a", attrs={"name": anchor}))

            if not h3_tag:
                continue

            section_lines = [f"#{anchor}", h3_tag.get_text(strip=True)]
            for sibling in h3_tag.find_all_next():
                if sibling.name == "h3" and sibling.find("a") and sibling.find("a").get("name") in anchors:
                    break
                if sibling.name == "tr":
                    section_lines.append(sibling.get_text(separator="\n", strip=True))

            chunk = "\n".join(section_lines).strip()
            if chunk:
                chunks.append(chunk)

        # Step 3: Fallback if no section-based chunks found
        if not chunks:
            plain_text = soup.get_text(separator="\n", strip=True)
            return self.custom_markdown_chunking(plain_text)

        return chunks
