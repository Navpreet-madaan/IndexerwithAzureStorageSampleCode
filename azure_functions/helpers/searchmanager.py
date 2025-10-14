"""_summary_

    Returns:
        _type_: return the response of the operation
"""

from azure.search.documents.indexes.models import (
    HnswVectorSearchAlgorithmConfiguration,
    PrioritizedFields,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticSettings,
    SimpleField,
    VectorSearch,
    VectorSearchAlgorithmKind,
    VectorSearchProfile,
)
from helpers.configmapper import ConfigMapper
from helpers.searchinfo import SearchInfo


class SearchManager:
    """
    Class to manage a search service. It can create indexes, and update
    or remove sections stored in these indexes
    To learn more, please visit
    https://learn.microsoft.com/azure/search/search-what-is-azure-search
    """

    def __init__(
        self, _searchservice, _index_name, _credential, config_mapper: ConfigMapper
    ):
        """_summary_

        Args:
            _searchservice (_type_): search service
            _index_name (_type_): index name
            _credential (_type_): default credential
            config_mapper (__ConfigMapper__): config
        """
        self.search_info = SearchInfo(
            endpoint=f"{_searchservice}",
            credential=_credential,
            index_name=_index_name,
            verbose=config_mapper.verbose,
        )

        self.search_analyzer_name = config_mapper.search_analyzer_name
        self.use_acls = config_mapper.use_acls
        self.search_images = config_mapper.search_images
        self.algorithm = config_mapper.algorithm
        self.embedding_config = config_mapper.embedding_config
        self.id_field = config_mapper.id_field
        self.content_field = config_mapper.content_field
        self.embedding_field = config_mapper.embedding_field
        self.title_field = config_mapper.title_field
        self.url_field = config_mapper.url_field
        self.file_path_field = config_mapper.file_path_field
        self.oids_field = config_mapper.oids_field
        self.groups_field = config_mapper.groups_field
        self.documentid_field = config_mapper.documentid_field
        self.image_emedd_field = config_mapper.image_emedd_field
        self.metric = config_mapper.metric
        self.field_type = config_mapper.field_type
        self.vector_dim = config_mapper.vector_search_dimensions
        self.vector_dim2 = config_mapper.vector_search_dim

    def _create_index(
        self,
        index_name,
        documents=None,
    ):
        """_summary_

        Args:
            index_name (_type_): name of the index
            documents (_type_): documents to be added
        """
        with self.search_info.create_search_index_client() as search_client:
            # Example document to infer fields
            if documents is not None and (
                documents[0].get("metadata") or documents[0].get("accessrights")
            ):
                # Dynamically create fields based on the document keys
                fields = []
                for key, value in documents[0].items():
                    field_type = self.get_field_type(value)
                    if key == "id":
                        fields.append(
                            SimpleField(
                                name=key, type=field_type, key=True, filterable=True
                            )
                        )
                    elif key == "metadata":
                        fields.append(
                            SearchableField(
                                name=key,
                                type=SearchFieldDataType.Collection(
                                    SearchFieldDataType.String
                                ),
                            )
                        )
                    elif key == "accessrights":
                        fields.append(
                            SimpleField(
                                name=key,
                                type=SearchFieldDataType.Collection(
                                    SearchFieldDataType.String
                                ),
                                filterable=True,
                            )
                        )
                    elif isinstance(value, str) and len(value) > 200:
                        fields.append(
                            SearchableField(
                                name=key,
                                type=field_type,
                                analyzer_name=self.search_analyzer_name,
                            )
                        )
                    elif isinstance(value, list):
                        fields.append(
                            SearchField(
                                name=key,
                                type=field_type,
                                hidden=False,
                                searchable=True,
                                filterable=False,
                                sortable=False,
                                facetable=False,
                                vector_search_dimensions=self.vector_dim,
                                vector_search_profile=self.embedding_config,
                            )
                        )
                    else:
                        fields.append(
                            SimpleField(
                                name=key,
                                type=field_type,
                                facetable=True,
                                filterable=True,
                            )
                        )
            else:
                fields = [
                    SimpleField(name=self.id_field, type=self.field_type, key=True),
                    SearchableField(
                        name=self.content_field,
                        type=self.field_type,
                        analyzer_name=self.search_analyzer_name,
                    ),
                    SearchField(
                        name=self.embedding_field,
                        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        hidden=False,
                        searchable=True,
                        filterable=False,
                        sortable=False,
                        facetable=False,
                        vector_search_dimensions=self.vector_dim,
                        vector_search_profile=self.embedding_config,
                    ),
                    SimpleField(
                        name=self.title_field,
                        type=self.field_type,
                        filterable=True,
                        facetable=True,
                    ),
                    SimpleField(
                        name=self.url_field,
                        type=self.field_type,
                        filterable=True,
                        facetable=True,
                    ),
                    SimpleField(
                        name=self.file_path_field,
                        type=self.field_type,
                        filterable=True,
                        facetable=True,
                    ),
                    SimpleField(
                        name=self.documentid_field,
                        type=self.field_type,
                        filterable=True,
                        facetable=True,
                    ),
                ]
            if self.use_acls:
                fields.append(
                    SimpleField(
                        name=self.oids_field,
                        type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                        filterable=True,
                    )
                )
                fields.append(
                    SimpleField(
                        name=self.groups_field,
                        type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                        filterable=True,
                    )
                )
            if self.search_images:
                fields.append(
                    SearchField(
                        name=self.image_emedd_field,
                        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        hidden=False,
                        searchable=True,
                        filterable=False,
                        sortable=False,
                        facetable=False,
                        vector_search_dimensions=self.vector_dim2,
                        vector_search_profile=self.embedding_config,
                    ),
                )

            index = SearchIndex(
                name=index_name,
                fields=fields,
                semantic_settings=SemanticSettings(
                    configurations=[
                        SemanticConfiguration(
                            name="default",
                            prioritized_fields=PrioritizedFields(
                                title_field=None,
                                prioritized_content_fields=[
                                    SemanticField(
                                        field_name=self.content_field,
                                    )
                                ],
                            ),
                        )
                    ]
                ),
                vector_search=VectorSearch(
                    algorithms=[
                        HnswVectorSearchAlgorithmConfiguration(
                            name=self.algorithm,
                            kind=VectorSearchAlgorithmKind.HNSW,
                        )
                    ],
                    profiles=[
                        VectorSearchProfile(
                            name=self.embedding_config,
                            algorithm=self.algorithm,
                        ),
                    ],
                ),
            )
            search_client = self.search_info.create_search_index_client()
            if index_name not in ([name for name in search_client.list_index_names()]):
                if self.search_info.verbose:
                    search_client.create_index(index)

    def _update_content(self, documents, index_name, doc_id, index_update):
        with self.search_info.create_search_client(index_name) as client:
            if index_update:
                self.remove_content(index_name, doc_id)
            _response = client.upload_documents(documents)
            return _response

    def add(
        self,
        index_name,
        doc_id,
        index_update,
        documents,
    ):
        """_summary_

        Args:
            Index_name (_type_): index name to be created
            doc_id (_type_): Document ID
            index_update (_type_): index update
            documents (_type_): documents to be added

        Returns:
            _type_: return the response of the operation
        """
        __response = False
        self._create_index(index_name, documents)
        __response = self._update_content(documents, index_name, doc_id, index_update)
        return __response

    # get_field_type method based on data type
    def get_field_type(self, value):
        """_summary_

        Args:
            value (_type_): field value

        Returns:
            _type_: returning type of field
        """
        if isinstance(value, float):
            return SearchFieldDataType.Double
        elif isinstance(value, list):
            return SearchFieldDataType.Collection(SearchFieldDataType.Single)
            # Add more cases as needed for other data types
        return SearchFieldDataType.String

    # Remove content from the search index
    def remove_content(self, index_name, doc_id):
        """_summary_

        Args:
            index_name (_type_): index name
            doc_id (_type_): document ID

        Returns:
            _type_: return the number of documents removed
        """
        with self.search_info.create_search_client(index_name) as client:
            _filter = None
            if doc_id is not None:
                _filter = f"documentId eq '{doc_id}'"
            _search_documents = list(
                client.search(search_text="", filter=_filter, include_total_count=True)
            )
            if len(_search_documents) > 0:
                _documents_to_remove = []
                for document in _search_documents:
                    _documents_to_remove.append({"id": document["id"]})
                _removed_docs = client.delete_documents(_documents_to_remove)
                return len(_removed_docs)
            else:
                return 0
