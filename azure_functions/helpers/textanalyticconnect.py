"""Text Analytics Connect

    Returns:
        _type_: returns the text analytics manager
"""

from azure.ai.textanalytics import TextAnalyticsClient


class TextAnalyticsConnect:
    """Text Analytic connect class for connecting with azure analytic service"""

    def __init__(self, lang_endpoint_secret, credentials):
        self.lang_endpoint_secret = lang_endpoint_secret
        self.credentials = credentials

    def authenticate_client(self):
        """Authenticate the text analytics client

        Returns:
            _type_: returns the text analytics client
        """
        return TextAnalyticsClient(
            endpoint=self.lang_endpoint_secret, credential=self.credentials
        )
