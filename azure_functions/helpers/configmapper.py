"""ConfigMapper class to set the
configuration for the embeddings and index"""


class ConfigMapper:
    """Config Mapper class for setting the configuration and reading from
    config and env files
    """

    def __init__(
        self,
        _=None,
    ):
        # Embeddings configuration
        self.max_batch_size = 1000
        self.has_image_embeddings = True
        self.verbose = True
        self.sentence_endings = [".", "!", "?"]
        self.word_breaks = [
            ",",
            ";",
            ":",
            " ",
            "(",
            ")",
            "[",
            "]",
            "{",
            "}",
            "\t",
            "\n",
        ]
        self.max_section_length = 1000
        self.sentence_search_limit = 100
        self.section_overlap = 100
        self.openai_deployment = "text-embedding-ada-002"
        self.openai_model = "text-embedding-ada-002"
        self.batch_model = {
            "text-embedding-ada-002": {
                "token_limit": 8100,
                "max_batch_size": 16,
            }
        }
        self.open_ai_api_version = "2024-02-01"
        self.disable_batch_vectors = False
        self.category = None
        # Index configuration
        self.search_analyzer_name = None
        self.use_acls = False
        self.search_images = False
        self.verbose = True
        self.algorithm = "hnsw_config"
        self.embedding_config = "embedding_config"
        self.id_field = "id"
        self.content_field = "content"
        self.embedding_field = "embedding"
        self.title_field = "title"
        self.url_field = "url"
        self.file_path_field = "filepath"
        self.oids_field = "oids"
        self.groups_field = "groups"
        self.documentid_field = "documentId"
        self.image_emedd_field = "imageEmbedding"
        self.metric = "cosine"
        self.field_type = "Edm.String"
        self.vector_search_dimensions = 1536
        self.vector_search_dim = 1024

        # RedactPii configuration
        self.redact_pii = False
        self.language = "en"
