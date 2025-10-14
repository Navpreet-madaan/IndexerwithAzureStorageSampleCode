"""Question Generator module.

    Returns:
        _type_: return the results based on API request
"""

import openai

from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from common.handlers import KeyVaultHandler


class QuestionGenerator:
    """Question Generator class for
    generating questions based on the context given"""

    def __init__(self) -> None:
        _key_vault_handler = KeyVaultHandler()
        self._open_ai_deployment_name = _key_vault_handler.get_secret(
            secret_name="openai-deployment-name-for-question-generation",
        )
        self._open_ai_api_version = _key_vault_handler.get_secret(
            secret_name="openai-api-version-for-question-generation",
        )
        self._open_ai_endpoint = _key_vault_handler.get_secret(
            secret_name="openai-endpoint",
        )

    def _call_openai(
        self,
        system_msg,
        user_msg,
        context,
    ):
        messages = [
            {
                "role": "system",
                "content": system_msg,
            },
            {
                "role": "user",
                "content": user_msg + "\n" + context,
            },
        ]

        client = openai.AzureOpenAI(
            azure_endpoint=self._open_ai_endpoint,
            azure_ad_token_provider=get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default",
            ),
            api_version=self._open_ai_api_version,
        )

        # Call the OpenAI chat completion API to generate an answer
        _completion = client.chat.completions.create(
            messages=messages,
            model=self._open_ai_deployment_name,
            temperature=0.4,
        )
        # Append the result to the answers_df DataFrame
        _content = _completion.choices[0].message.content.strip()
        return _content

    def generate(
        self,
        content,
    ):
        """Generate a question based on the context given"""
        # Your existing logic to generate a question
        _system_msg = """You're a question generator that generates questions
                        based on the context given.
                        You should not mention Vodafone or
                        any other company name.
                        You should generate questions with less than 10 words.
                        You should use simple language.
                        RESPOND **ONLY** IN EUROPEAN PORTUGUESE, PT-PT"""
        _user_msg = """Generate a question of less than 10 words based on
            the following context:"""
        _context = content
        _generated_question = self._call_openai(
            system_msg=_system_msg,
            user_msg=_user_msg,
            context=_context,
        )
        return _generated_question
