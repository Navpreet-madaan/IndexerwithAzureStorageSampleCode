"Key Vault Handler"
import os

from azure.identity import DefaultAzureCredential

from azure.keyvault.secrets import SecretClient


class KeyVaultHandler:
    "To return secrets from the key vault"

    def __init__(
        self,
    ) -> None:
        self.key_vault_url = os.environ["KEY_VAULT_URL"]

    def _get_secret(
        self,
        **kwargs,
    ):
        _key_vault_url = self.key_vault_url
        _secret_name = kwargs.get("secret_name")
        _credential = DefaultAzureCredential()
        _secret_client = SecretClient(
            _key_vault_url,
            _credential,
        )
        _retrieved_secret = _secret_client.get_secret(
            _secret_name,
        )
        _secret_value = _retrieved_secret.value

        return _secret_value

    def get_secret(
        self,
        **kwargs,
    ):
        "Get secrets from key vault"
        _secret_value = self._get_secret(**kwargs)
        return _secret_value
