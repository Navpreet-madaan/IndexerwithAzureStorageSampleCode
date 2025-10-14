"Azure Open Ai emeddings"
import time

from typing import Optional
from azure.core.credentials import AccessToken
from openai import AzureOpenAI, OpenAI

from helpers.configmapper import ConfigMapper
from common.embeddings import OpenAIEmbeddings


class AzureOpenAIEmbeddingService(OpenAIEmbeddings):
    """
    Class for using Azure OpenAI embeddings
    To learn more please visit
    https://learn.microsoft.com/azure/ai-services/openai/concepts/understand-embeddings
    """

    def __init__(self, open_ai_service: str, credential, config_mapper: ConfigMapper):
        super().__init__(
            config_mapper.openai_model,
            config_mapper.batch_model,
            config_mapper.disable_batch_vectors,
            config_mapper.verbose,
        )
        self.open_ai_service = open_ai_service
        self.open_ai_deployment = config_mapper.openai_deployment
        self.credential = credential
        self.token: Optional[AccessToken] = None
        self.open_ai_api_version = config_mapper.open_ai_api_version

    def create_client(self) -> OpenAI:
        return AzureOpenAI(
            azure_endpoint=f"{self.open_ai_service}",
            azure_deployment=self.open_ai_deployment,
            api_key=self.wrap_credential(),
            api_version=self.open_ai_api_version,
        )

    def wrap_credential(self) -> str:
        "Wrap credential for Key Vault"
        if not self.token or self.token.expires_on <= time.time():
            self.token = self.credential.get_token(
                "https://cognitiveservices.azure.com/.default"
            )

        return self.token.token
