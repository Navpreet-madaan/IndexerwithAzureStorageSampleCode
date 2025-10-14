"""Question Generator module.

    Returns:
        _type_: return the results based on API request
"""

import openai

from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
    wait_fixed,
)

FIXED_WAIT = 5
RETRY_ATTEMPTS = 3


def is_rate_limit_error(exception):
    return isinstance(exception, openai.RateLimitError)


class QuestionGenerator:
    """Question Generator class for
    generating questions based on the context given"""

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        open_ai_endpoint = kwargs.get("open_ai_endpoint")
        open_ai_api_version = kwargs.get("open_ai_api_version")
        self.open_ai_deployment_name = kwargs.get("open_ai_deployment_name")
        self._logger = kwargs.get("logger")
        self.temperature = float(kwargs.get("temperature"))
        self.client = openai.AzureOpenAI(
            azure_endpoint=open_ai_endpoint,
            azure_ad_token_provider=get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default",
            ),
            api_version=open_ai_api_version,
        )

    def _wait_till_retry_after(self, retry_state):
        import time

        response = retry_state.outcome.result()
        retry_after = int(
            response.headers.get(
                "Retry-After",
                FIXED_WAIT,
            )
        )
        self._logger.info(
            "Retrying after %d seconds as per Retry-After header", retry_after
        )
        time.sleep(retry_after)

    @retry(
        retry=retry_if_exception(is_rate_limit_error),
        wait=_wait_till_retry_after,
        stop=stop_after_attempt(RETRY_ATTEMPTS),
    )
    def _completion_with_retry_after(self, **kwargs):
        return self.client.chat.completions.create(**kwargs)

    def _call_openai(self, **kwargs):
        messages = [
            {
                "role": "system",
                "content": kwargs.get("system_msg"),
            },
            {
                "role": "user",
                "content": kwargs.get("user_msg") + "\n" + kwargs.get("context"),
            },
        ]
        # Call the OpenAI chat completion API to generate an answer
        _completion = self._completion_with_retry_after(
            messages=messages,
            model=self.open_ai_deployment_name,
            temperature=self.temperature,
        )
        # Append the result to the answers_df DataFrame
        _content = _completion.choices[0].message.content.strip()
        return _content

    def generate(
        self,
        content,
        intent,
    ):
        """Generate a question based on the context given"""
        # Your existing logic to generate a question
        _system_msg = """You're a question generator that generates questions
                     based on the context and intent provided.
                     You should not mention Vodafone or
                     any other company name.
                     You should generate questions with less than 10 words.
                     You should use simple language.
                     RESPOND **ONLY** IN PORTUGUESE."""
        if intent.lower() == "unknown":
            # Adjust user message for generic question generation
            _user_msg = """Generate a generic question of less than 10 words."""
        else:
            # Adjust user message to include context and intent
            _user_msg = """Generate a question of less than 10 words based on the following context and intent:
                - Context: {context}
                - Intent: {intent}"""
            # Format the user message with context and intent
            _user_msg = _user_msg.format(context=content, intent=intent)
        # Call OpenAI with the modified messages
        _generated_question = self._call_openai(
            system_msg=_system_msg, user_msg=_user_msg, context=content
        )
        return _generated_question
