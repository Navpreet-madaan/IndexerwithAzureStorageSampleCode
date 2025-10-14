"""search Info class

    Returns:
        _type_: used for azure search services
"""

from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient


class SearchInfo:
    """
    Class representing a connection to a search service
    To learn more, please visit
    https://learn.microsoft.com/azure/search/search-what-is-azure-search
    """

    def __init__(
        self,
        endpoint: str,
        credential,
        index_name: str,
        verbose: bool = False,
    ):
        self.endpoint = endpoint
        self.credential = credential
        self.index_name = index_name
        self.verbose = verbose

    def create_search_client(self, index_name) -> SearchClient:
        """_summary_

        Args:
            index_name (_type_): index name

        Returns:
            SearchClient: search client for the index
        """
        return SearchClient(
            endpoint=self.endpoint,
            index_name=index_name,
            credential=self.credential,
        )

    def create_search_index_client(self) -> SearchIndexClient:
        """_summary_

        Returns:
            SearchIndexClient: search index client
        """
        return SearchIndexClient(
            endpoint=self.endpoint,
            credential=self.credential,
        )
