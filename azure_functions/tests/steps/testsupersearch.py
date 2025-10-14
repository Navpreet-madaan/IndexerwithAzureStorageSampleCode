"""Super Search Test Module and we are using the behave
library to write BDD tests"""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch
from behave import given, then, when  # pylint: disable=no-name-in-module

import logging

from supersearch import SuperSearch
from supersearch.spdpfm import SpeedPerformAPI
from supersearch.articleinfo import ArticleInfo
from supersearch.document import Document
from supersearch.metadata import DocumentManager
from supersearch.qgen import QuestionGenerator
from supersearch.spdpfm import SpeedPerformAPI
from supersearch.articleinfo import ArticleJSONDecoder

logging.getLogger("azure").setLevel(logging.WARNING)


def _get_list_of_articles():
    """getting a list of articles from the test data

    Returns:
        _type_: list of articles
    """
    with open(
        "tests/data/supersearch/speedperform/list.json",
        "r",
        encoding="utf-8",
    ) as fd:
        _list_of_articles = fd.read()
        _list_of_articles = ArticleInfo.from_json(_list_of_articles)
        return _list_of_articles


class JSONDecoder(json.JSONDecoder):
    """JSON Decoder class"""

    def __init__(self):
        """JSON Decoder class constructor"""
        json.JSONDecoder.__init__(
            self,
            object_hook=JSONDecoder.from_dict,
        )

    @staticmethod
    def from_dict(d):
        """
        Convert the dictionary item to an object
        """
        _last_modified = datetime.strptime(
            d["LastDownloadedTime"],
            "%Y-%m-%dT%H:%M:%SZ",
        )
        _updated_at = datetime.strptime(
            d["UpdatedAt"],
            "%Y-%m-%dT%H:%M:%SZ",
        )
        _created_at = datetime.strptime(
            d["CreatedAt"],
            "%Y-%m-%dT%H:%M:%SZ",
        )

        _document_metadata = Document()
        _document_metadata.id = d["ID"]
        _document_metadata.version = d["Version"]
        _document_metadata.checksum = d["CheckSum"]
        _document_metadata.last_modified = _last_modified
        _document_metadata.status = d["Status"]
        _document_metadata.updated_at = _updated_at
        _document_metadata.created_at = _created_at
        return _document_metadata


def _get_list_of_documents():
    """getting a list of documents from the test data"""
    with open(
        "tests/data/supersearch/metadata/list.json",
        "r",
        encoding="utf-8",
    ) as fd:
        _rows = json.load(fd, cls=JSONDecoder)
        return _rows


def _get_article_detail(article_id):
    """getting an article detail from the test data"""
    with open(
        f"tests/data/supersearch/speedperform/{article_id}.json",
        "r",
        encoding="utf-8",
    ) as fd:
        _content = fd.read()
        return _content, "dummy_url"


@given("we get a list of articles from SpeedPerform")
def step_impl(
    context,
):
    """we get a list of articles from SpeedPerform"""
    with patch("common.handlers.KeyVaultHandler.get_secret") as mocksecret:
        mocksecret.return_value = "dummy"
        with patch(
            "supersearch.spdpfm.SpeedPerformAPI.list"
        ) as mock_get_list_of_articles:
            mock_get_list_of_articles.return_value = _get_list_of_articles()

            speed_perform_api = SpeedPerformAPI()
            context.speed_perform_api = speed_perform_api
            context.speed_perform_list = speed_perform_api.list()


@when("we get current document metadata")
def step_impl(  # noqa: F811  # pylint: disable=function-redefined
    context,
):
    """we get current document metadata"""
    with patch("common.handlers.KeyVaultHandler.get_secret") as mock_secret:
        mock_secret.return_value = "dummy"
        with patch(
            "supersearch.metadata.DocumentManager.list"
        ) as mock_get_list_of_documents:
            mock_get_list_of_documents.return_value = _get_list_of_documents()
            _document_manager = DocumentManager()
            _list = _document_manager.list()
            assert _list is not None
            context.metadata_list = _list


@then("we compare the differences between the list")
def step_impl(  # noqa: F811  # pylint: disable=function-redefined
    context,
):
    """we compare the differences between the list"""
    _speed_perform_list = context.speed_perform_list
    _metadata_list = context.metadata_list

    with patch(
        "common.handlers.KeyVaultHandler.get_secret"
    ) as mock_get_secret:  # noqa: 501
        mock_get_secret.return_value = "dummy"
        with patch(
            "supersearch.spdpfm.SpeedPerformAPI.list"
        ) as mock_get_list_of_articles:
            mock_get_list_of_articles.return_value = _get_list_of_articles()
            with patch(
                "supersearch.metadata.DocumentManager.list"
            ) as mock_get_list_of_documents:
                mock_get_list_of_documents.return_value = (
                    _get_list_of_documents()
                )  # noqa: 501
                _super_search = SuperSearch()
                _speed_perform_list = _super_search.get_speed_perform_list()
                _metadata_list = _super_search.get_metadata_list()
                _items_to_add, _items_to_update, _items_to_delete, _ = (
                    _super_search.get_delta(
                        _speed_perform_list,
                        _metadata_list,
                    )
                )

                assert len(_items_to_add) == 2
                assert len(_items_to_update) == 1
                assert len(_items_to_delete) == 1


@given("we have a set of articles")
def step_impl(  # noqa: F811  # pylint: disable=function-redefined
    context,
):
    """we have a set of articles"""
    with patch(
        "common.handlers.KeyVaultHandler.get_secret"
    ) as mock_get_secret:  # noqa: 501
        mock_get_secret.return_value = "dummy"
        with patch(
            "supersearch.spdpfm.SpeedPerformAPI.list"
        ) as mock_get_list_of_articles:
            mock_get_list_of_articles.return_value = _get_list_of_articles()
            with patch(
                "supersearch.metadata.DocumentManager.list"
            ) as mock_get_list_of_documents:
                mock_get_list_of_documents.return_value = (
                    _get_list_of_documents()
                )  # noqa: 501

                _super_search = SuperSearch()
                _speed_perform_list = _super_search.get_speed_perform_list()
                _metadata_list = _super_search.get_metadata_list()
                _items_to_add, _items_to_update, _items_to_delete, _ = (
                    _super_search.get_delta(
                        _speed_perform_list,
                        _metadata_list,
                    )
                )
                context.items_to_add = _items_to_add
                context.items_to_update = _items_to_update
                context.items_to_delete = _items_to_delete


@given("a QuestionGenerator instance")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    context.question_generator = QuestionGenerator()


@given("a system message, user message, and context")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    context.system_msg = "System message for testing"
    context.user_msg = "User message for testing"
    context.context_msg = "Context message for testing"


@given("a content message")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    context.content = "This is a test context for generating a question."


@given("a SpeedPerformAPI instance")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    context.speedperform_api = SpeedPerformAPI()


@given("an article ID")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    context.article_id = 1


@when("the get method is called")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        _json_str = json.dumps(
            [
                {
                    "id": 1,
                    "title": "Test Article",
                    "revisionId": 1,
                    "lastModified": datetime.strftime(
                        datetime.utcnow(),
                        "%Y-%m-%dT%H:%M:%SZ",
                    ),
                    "type": "dummy",
                    "description": "dummy",
                    "status": "dummy",
                    "publicLink": "dummy",
                }
            ]
        )
        mock_response.json.return_value = json.loads(
            _json_str,
            cls=ArticleJSONDecoder,
        )
        mock_get.return_value = mock_response
        context.result = context.speedperform_api.get(context.article_id)


@when("the list method is called")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        import json

        _json_str = json.dumps(
            [
                {
                    "id": 1,
                    "title": "Test Article",
                    "revisionId": 1,
                    "lastModified": datetime.strftime(
                        datetime.utcnow(),
                        "%Y-%m-%dT%H:%M:%SZ",
                    ),
                    "type": "dummy",
                    "description": "dummy",
                    "status": "dummy",
                    "publicLink": "dummy",
                }
            ]
        )
        mock_response.json.return_value = json.loads(
            _json_str,
            cls=ArticleJSONDecoder,
        )
        mock_get.return_value = mock_response
        context.result = context.speedperform_api.list()


@when("the generate method is called")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    with patch("openai.AzureOpenAI") as MockOpenAI:
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content.strip.return_value = (
            "Generated question"
        )
        mock_client.chat.completions.create.return_value = mock_completion
        MockOpenAI.return_value = mock_client

        context.result = context.question_generator.generate(
            content=context.content,
        )


@when("the OpenAI API is called")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    with patch("openai.AzureOpenAI") as MockOpenAI:
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content.strip.return_value = (
            "Generated question"
        )
        mock_client.chat.completions.create.return_value = mock_completion
        MockOpenAI.return_value = mock_client

        context.result = context.question_generator._call_openai(
            system_msg=context.system_msg,
            user_msg=context.user_msg,
            context=context.context_msg,
        )


@when("we add them to the search index")
def step_impl(  # noqa: F811  # pylint: disable=function-redefined
    context,
):
    """we add them to the search index"""
    with patch(
        "common.handlers.KeyVaultHandler.get_secret"
    ) as mock_get_secret:  # noqa: 501
        mock_get_secret.return_value = "dummy"
        _items_to_add = context.items_to_add
        assert len(_items_to_add) == 2
        with patch("supersearch.spdpfm.SpeedPerformAPI.get") as mock_article:
            _item_to_add: Document = _items_to_add[0]
            mock_article.return_value = _get_article_detail(
                article_id=_item_to_add.id,
            )
            with patch(
                "common.embeddings.OpenAIEmbeddings.create_embedding_single"
            ) as mock_get_embedding:
                mock_get_embedding.return_value = [0.1, 0.2]
                with patch(
                    "supersearch.qgen.QuestionGenerator.generate"
                ) as mock_question_generator_generate:
                    mock_question_generator_generate.return_value = "dummy"
                    with patch(
                        "supersearch.qgen.QuestionGenerator._call_openai"
                    ) as mock_question_generator_call:
                        mock_question_generator_call.return_value = "dummy"
                        with patch(
                            "helpers.searchmanager.SearchManager.add"
                        ) as mock_add_document:
                            mock_add_document.return_value = MagicMock()
                            with patch(
                                "supersearch.metadata.DocumentManager.save"
                            ) as mock_docmgr_save:  # noqa: 501
                                mock_docmgr_save.return_value = "dummy"
                                _super_search = SuperSearch()
                                _super_search.index_article(
                                    article_info=_item_to_add,
                                    op="add",
                                )


@when("we update them to the search index")
def step_impl(  # noqa: F811  # pylint: disable=function-redefined
    context,
):
    """we update them to the search index"""
    with patch(
        "common.handlers.KeyVaultHandler.get_secret"
    ) as mock_get_secret:  # noqa: 501
        mock_get_secret.return_value = "dummy"
        _items_to_update = context.items_to_update
        assert len(_items_to_update) == 1
        with patch("supersearch.spdpfm.SpeedPerformAPI.get") as mock_article:
            _item_to_update: Document = _items_to_update[0]
            mock_article.return_value = _get_article_detail(
                article_id=_item_to_update.id,
            )
            with patch(
                "common.embeddings.OpenAIEmbeddings.create_embedding_single"
            ) as mock_get_embedding:
                mock_get_embedding.return_value = [0.1, 0.2]
                with patch(
                    "supersearch.qgen.QuestionGenerator.generate"
                ) as mock_question_generator_generate:
                    mock_question_generator_generate.return_value = "dummy"
                    with patch(
                        "helpers.searchmanager.SearchManager.add"
                    ) as mock_add_document_to_index:
                        mock_add_document_to_index.return_value = MagicMock()
                        with patch(
                            "supersearch.metadata.DocumentManager.save"
                        ) as mock_documentmanager_save:  # noqa: 501
                            mock_documentmanager_save.return_value = "dummy"
                            _super_search = SuperSearch()
                            _super_search.index_article(
                                article_info=_item_to_update,
                                op="update",
                            )


@when("we delete them to the search index")
def step_impl(  # noqa: F811  # pylint: disable=function-redefined
    context,
):
    """we delete them to the search index"""
    with patch(
        "common.handlers.KeyVaultHandler.get_secret"
    ) as mock_get_secret:  # noqa: 501
        mock_get_secret.return_value = "dummy"
        _items_to_delete = context.items_to_delete
        assert len(_items_to_delete) == 1
        with patch(
            "supersearch.spdpfm.SpeedPerformAPI.get"
        ) as mock_get_article:  # noqa: 501
            mock_get_article.return_value = "dummy"
            _item_to_delete: Document = _items_to_delete[0]
            with patch(
                "helpers.searchmanager.SearchManager.remove_content"  # noqa: 501
            ) as mock_delete_document_to_index:
                mock_delete_document_to_index.return_value = MagicMock()
                with patch(
                    "supersearch.metadata.DocumentManager.retire"
                ) as mock_documentmanager_retire:  # noqa: 501
                    mock_documentmanager_retire.return_value = "dummy"
                    _super_search = SuperSearch()
                    _super_search.process_item_to_delete(
                        item_to_delete=_item_to_delete,
                        op="delete",
                    )


@then("they exist in the metadata")
def step_impl(  # noqa: F811  # pylint: disable=function-redefined
    context,
):
    """they exist in the metadata"""
    context.return_value = True
    pass


@then("the result should be the generated question")
def step_impl(context):  # noqa: F811  # pylint: disable=function-redefined
    assert (
        context.result == "Generated question"
    ), f"Expected 'Generated question', but got {context.result}"


@then("the result should be the article details")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    expected_result = "sometext", "dummy_url"
    assert (
        context.result is not None
    ), f"Expected {expected_result}, but got {context.result}"


@then("the result should be a list of articles")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    expected_result = [
        ArticleInfo(
            id=1,
            revision_id="1",
            type="dummy",
            title="Test Article",
            description="dummy",
            last_modified=datetime.utcnow(),
            status="dummy",
            public_link="dummy",
        )
    ]
    assert (
        context.result[0].id == expected_result[0].id
    ), f"Expected {expected_result}, but got {context.result}"
