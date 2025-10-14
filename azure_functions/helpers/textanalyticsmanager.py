"""Text Analytics Manager

    Returns:
        _type_: returns the text analytics manager
"""

from helpers.configmapper import ConfigMapper
from helpers.textanalyticconnect import TextAnalyticsConnect


class TextAnalyticsManager:
    """Text Analytic manager class for redacting PII content"""

    def __init__(
        self,
        _lang_endpoint_secret,
        _credentials,
        content,
        config_mapper: ConfigMapper,
    ):

        self.text_analytics_connect = TextAnalyticsConnect(
            lang_endpoint_secret=_lang_endpoint_secret,
            credentials=_credentials,
        )

        self.language = config_mapper.language
        self.redact_pii_flag = config_mapper.redact_pii
        self.client = self.text_analytics_connect.authenticate_client()
        self.content = content

    # use inbuilt method to identify and mask PII content
    def pii_data(self, content):
        """PII Recognition

        Returns:
            _type_: returns the redacted content
        """
        if self.redact_pii_flag:
            documents = [content]
            response = self.client.recognize_pii_entities(
                documents, language=self.language
            )
            result = [doc for doc in response if not doc.is_error]
            for doc in result:
                redacted_content = doc.redacted_text
            return redacted_content
        else:
            return content
