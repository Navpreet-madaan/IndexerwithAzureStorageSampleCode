"""Secret Handlers for Key vault

    Returns:
        _type_: returns the secrets
"""

from common.handlers import KeyVaultHandler
from common import KeyVault


class SecretsHandler:
    """Handling all the secrets from key vault"""

    def __init__(self):
        self._key_vault_handler = KeyVaultHandler()

    def get_secrets(self):
        """_summary_

        Returns:
            _type_: returns the secrets
        """
        # Get secrets from Azure Key Vault & account key
        forms_recognizer_service = self._key_vault_handler.get_secret(
            secret_name=KeyVault.document_intelligent_endPoint_secret,
        )
        storage_account_base = self._key_vault_handler.get_secret(
            secret_name=KeyVault.storage_account_basePath_secret,
        )
        sql_server_name = self._key_vault_handler.get_secret(
            secret_name=KeyVault.sql_server_name_secret,
        )
        sql_db_name = self._key_vault_handler.get_secret(
            secret_name=KeyVault.sql_db_name_secret,
        )
        open_ai_service = self._key_vault_handler.get_secret(
            secret_name=KeyVault.open_ai_service_secret_name,
        )
        app_inst_key = self._key_vault_handler.get_secret(
            secret_name=KeyVault.app_insights_instkey,
        )
        search_service = self._key_vault_handler.get_secret(
            secret_name=KeyVault.azure_ai_search_service,
        )
        index_name = self._key_vault_handler.get_secret(
            secret_name=KeyVault.azure_ai_search_index,
        )
        lang_endpoint_secret = self._key_vault_handler.get_secret(
            secret_name=KeyVault.lang_endpoint_secret,
        )
        upload_container_path = self._key_vault_handler.get_secret(
            secret_name=KeyVault.azure_container_path,
        )
        sharepoint_base_path = self._key_vault_handler.get_secret(
            secret_name=KeyVault.sharepoint_base_path,
        )
        return (
            forms_recognizer_service,
            storage_account_base,
            sql_server_name,
            sql_db_name,
            open_ai_service,
            app_inst_key,
            search_service,
            index_name,
            lang_endpoint_secret,
            upload_container_path,
            sharepoint_base_path,
        )
