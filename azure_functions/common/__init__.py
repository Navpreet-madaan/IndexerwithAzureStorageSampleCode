"Key valy class to return secrets from the key vault"


class KeyVault:
    "Key vault constants"
    # Document Intelligence Service constants
    document_intelligent_endPoint_secret = (
        "document-intelligence-endpoint"  # nosec #ignore on bandit scan
    )
    # Storage Blob constants
    storage_account_basePath_secret = (
        "landing-storage-account"  # nosec #ignore on bandit scan
    )
    # SQL Server constants
    sql_server_name_secret = "sql-server-name"  # nosec #ignore on bandit scan
    sql_db_name_secret = "sql-database-name"  # nosec #ignore on bandit scan
    open_ai_service_secret_name = "openai-endpoint"  # nosec #ignore on bandit
    app_insights_instkey = "app-insights-instkey"  # nosec #ignore on bandit
    lang_endpoint_secret = "ai-language-endpoint"  # nosec #ignore on bandit
    azure_ai_search_service = "ai-search-endpoint"  # nosec #ignore on bandit
    azure_ai_search_index = "ai-search-index"  # nosec #ignore on bandit scan
    azure_container_path = "container-path"  # nosec #ignore on bandit scan
    sharepoint_base_path = "sharepoint-base-path"  # nosec #ignore on bandit
