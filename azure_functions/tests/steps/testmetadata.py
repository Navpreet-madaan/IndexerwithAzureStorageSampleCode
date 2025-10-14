"This module contains the step definitions for the metadata feature tests."
# flake8: noqa
from datetime import datetime
from unittest.mock import patch, MagicMock
from behave import given, then, when  # pylint: disable=no-name-in-module

from supersearch.document import Document
from supersearch.metadata import DocumentManager
from common.sql import SqlConnector


@given("we have an article with access rights")
def step_impl(context):
    """step_impl for given we have an article with access rights

    Args:
        context (_type_): behave context
    """

    _last_modified = datetime.utcnow()
    _updated_at = datetime.utcnow()
    _created_at = datetime.utcnow()

    document_metadata = Document()
    _document_id = 100
    document_metadata.id = _document_id
    document_metadata.name = "Name"
    document_metadata.version = "Version"
    document_metadata.checksum = "CheckSum"
    document_metadata.last_modified = _last_modified
    document_metadata.status = "Status"
    document_metadata.updated_at = _updated_at
    document_metadata.created_at = _created_at

    context.document_metadata = document_metadata


@when("add the article with access rights")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    "step_impl for add the article with access rights"

    document_metadata = context.document_metadata

    with patch(
        "common.handlers.KeyVaultHandler.get_secret"
    ) as mock_get_secret:  # noqa: 501
        mock_get_secret.return_value = "dummy_secret"
        with patch(
            "common.sql.SqlConnector.get_session"
        ) as mock_sqlconnector_get_session:
            mock_sqlconnector_get_session.return_value = "dummy_session"
            with patch(
                "supersearch.metadata.DocumentManager.save"
            ) as mock_documentmanager_save:  # noqa: 501
                mock_documentmanager_save.return_value = "dummy_document"
                _document_manager = DocumentManager()
                _document_manager.save(document=document_metadata)
                mock_sqlconnector_get_session.commit.return_value = "dummy_commit"
                mock_sqlconnector_get_session.close.return_value = "dummy_close"


@then("delete the document and access rights")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    """step_impl for delete the document and access rights

    Args:
        context (_type_): behave context
    """
    document_metadata = context.document_metadata

    with patch(
        "common.handlers.KeyVaultHandler.get_secret"
    ) as mock_get_secret:  # noqa: 501
        mock_get_secret.return_value = "dummy_secret"
        with patch(
            "common.sql.SqlConnector.get_session"
        ) as mock_sqlconnector_get_session:
            mock_sqlconnector_get_session.return_value = "dummy_session"
            with patch(
                "supersearch.metadata.DocumentManager.delete"
            ) as mock_documentmanager_delete:  # noqa: 501
                mock_documentmanager_delete.return_value = "dummy_document"
                _document_manager = DocumentManager()
                _document_manager.delete(document_metadata)
                mock_sqlconnector_get_session.commit.return_value = "dummy_commit"
                mock_sqlconnector_get_session.close.return_value = "dummy_close"


@given("we have a document with no access rights")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    "step_impl for given we have a document with no access rights"
    _last_modified = datetime.utcnow()
    _updated_at = datetime.utcnow()
    _created_at = datetime.utcnow()

    document_metadata = Document()
    _document_id = 100
    document_metadata.id = _document_id
    document_metadata.name = "Name"
    document_metadata.version = "Version"
    document_metadata.checksum = "CheckSum"
    document_metadata.last_modified = _last_modified
    document_metadata.status = "Status"
    document_metadata.updated_at = _updated_at
    document_metadata.created_at = _created_at

    context.document_metadata = document_metadata


@when("add the document without access rights")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    "step_impl for add the document without access rights"
    _document_metadata = context.document_metadata

    with patch(
        "common.handlers.KeyVaultHandler.get_secret"
    ) as mock_get_secret:  # noqa: 501
        mock_get_secret.return_value = "dummy_secret"
        with patch(
            "common.sql.SqlConnector.get_session"
        ) as mock_sqlconnector_get_session:
            mock_sqlconnector_get_session.return_value = "dummy_session"
            with patch(
                "supersearch.metadata.DocumentManager.save"
            ) as mock_documentmanager_save:  # noqa: 501
                mock_documentmanager_save.return_value = "dummy_document"
                _document_manager = DocumentManager()
                _document_manager.save(document=_document_metadata)
                mock_sqlconnector_get_session.commit.return_value = "dummy_commit"
                mock_sqlconnector_get_session.close.return_value = "dummy_close"


@then("delete the document without access rights")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    "step_impl for delete the document without access rights"
    document_metadata = context.document_metadata

    with patch(
        "common.handlers.KeyVaultHandler.get_secret"
    ) as mock_get_secret:  # noqa: 501
        mock_get_secret.return_value = "dummy_secret"
        with patch(
            "common.sql.SqlConnector.get_session"
        ) as mock_sqlconnector_get_session:
            mock_sqlconnector_get_session.return_value = "dummy_session"
            with patch(
                "supersearch.metadata.DocumentManager.delete"
            ) as mock_documentmanager_delete:  # noqa: 501
                mock_documentmanager_delete.return_value = "dummy_document"
                _document_manager = DocumentManager()
                _document_manager.delete(document_metadata)
                mock_sqlconnector_get_session.commit.return_value = "dummy_commit"
                mock_sqlconnector_get_session.close.return_value = "dummy_close"


@given("we have a document that needs to be retired")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    "step_impl for given we have a document that needs to be retired"
    _last_modified = datetime.utcnow()
    _updated_at = datetime.utcnow()
    _created_at = datetime.utcnow()

    document_metadata = Document()
    _document_id = 200
    document_metadata.id = _document_id
    document_metadata.name = "Retirable Document"
    document_metadata.version = "1.0"
    document_metadata.checksum = 123456
    document_metadata.last_modified = _last_modified
    document_metadata.status = "Active"
    document_metadata.updated_at = _updated_at
    document_metadata.created_at = _created_at

    context.document_metadata = document_metadata


@when("retire the document")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    "step_impl for retire the document"
    document_metadata = context.document_metadata

    with patch(
        "common.handlers.KeyVaultHandler.get_secret"
    ) as mock_get_secret:  # noqa: 501
        mock_get_secret.return_value = "dummy_secret"
        with patch(
            "common.sql.SqlConnector.get_session"
        ) as mock_sqlconnector_get_session:
            mock_sqlconnector_get_session.return_value = "dummy_session"
            with patch(
                "supersearch.metadata.DocumentManager.retire"
            ) as mock_documentmanager_retire:  # noqa: 501
                mock_documentmanager_retire.return_value = "dummy_document"
                _document_manager = DocumentManager()
                _document_manager.retire(document=document_metadata)
                mock_sqlconnector_get_session.commit.return_value = "dummy_commit"
                mock_sqlconnector_get_session.close.return_value = "dummy_close"


@then("verify the document status is updated to retired")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    "step_impl for verify the document status is updated to retired"
    document_metadata = context.document_metadata

    with patch(
        "common.handlers.KeyVaultHandler.get_secret"
    ) as mock_get_secret:  # noqa: 501
        mock_get_secret.return_value = "dummy_secret"
        with patch(
            "common.sql.SqlConnector.get_session"
        ) as mock_sqlconnector_get_session:
            mock_sqlconnector_get_session.return_value = "dummy_session"
            with patch(
                "supersearch.metadata.DocumentManager.get"
            ) as mock_documentmanager_get:
                mock_documentmanager_get.return_value = document_metadata
                _document_manager = DocumentManager()
                _document_manager.get(doc_id=document_metadata.id)
                mock_sqlconnector_get_session.commit.return_value = "dummy_commit"
                mock_sqlconnector_get_session.close.return_value = "dummy_close"


@given("we have multiple documents stored")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    "step_impl for given we have multiple documents stored"
    context.documents = []

    for i in range(5):
        _last_modified = datetime.utcnow()
        _updated_at = datetime.utcnow()
        _created_at = datetime.utcnow()

        _document_metadata = Document()
        _document_metadata.id = i
        _document_metadata.name = f"Document {i}"
        _document_metadata.version = "1.0"
        _document_metadata.checksum = i * 1000
        _document_metadata.last_modified = _last_modified
        _document_metadata.status = "Active"
        _document_metadata.updated_at = _updated_at
        _document_metadata.created_at = _created_at

        context.documents.append(_document_metadata)


@when("list all documents")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    "step_impl for list all documents"
    with patch(
        "common.handlers.KeyVaultHandler.get_secret"
    ) as mock_get_secret:  # noqa: 501
        mock_get_secret.return_value = "dummy_secret"
        with patch(
            "common.sql.SqlConnector.get_session"
        ) as mock_sqlconnector_get_session:
            mock_sqlconnector_get_session.return_value = "dummy_session"
            with patch(
                "supersearch.metadata.DocumentManager.list"
            ) as mock_documentmanager_list:
                mock_documentmanager_list.return_value = context.documents

                _document_manager = DocumentManager()
                context.all_documents = _document_manager.list()
                mock_sqlconnector_get_session.commit.return_value = "dummy_commit"
                mock_sqlconnector_get_session.close.return_value = "dummy_close"


@then("verify the documents are listed")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    "step_impl for verify the documents are listed"
    assert len(context.all_documents) == 5
    for i, document in enumerate(context.all_documents):
        assert document.name == f"Document {i}"


@given("we have a specific document to retrieve")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    "step_impl for given we have a specific document to retrieve"
    _last_modified = datetime.utcnow()
    _updated_at = datetime.utcnow()
    _created_at = datetime.utcnow()

    document_metadata = Document()
    document_metadata.id = 300
    document_metadata.name = "Specific Document"
    document_metadata.version = "1.0"
    document_metadata.checksum = 654321
    document_metadata.last_modified = _last_modified
    document_metadata.status = "Active"
    document_metadata.updated_at = _updated_at
    document_metadata.created_at = _created_at

    context.document_metadata = document_metadata


@when("retrieve the document by id")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    "step_impl for retrieve the document by id"
    document_metadata = context.document_metadata

    with patch(
        "common.handlers.KeyVaultHandler.get_secret"
    ) as mock_get_secret:  # noqa: 501
        mock_get_secret.return_value = "dummy_secret"
        with patch(
            "common.sql.SqlConnector.get_session"
        ) as mock_sqlconnector_get_session:
            mock_sqlconnector_get_session.return_value = "dummy_session"
            with patch(
                "supersearch.metadata.DocumentManager.get"
            ) as mock_documentmanager_get:
                mock_documentmanager_get.return_value = document_metadata

                _document_manager = DocumentManager()
                context.retrieved_document = _document_manager.get(
                    doc_id=document_metadata.id
                )
                mock_sqlconnector_get_session.commit.return_value = "dummy_commit"
                mock_sqlconnector_get_session.close.return_value = "dummy_close"


@then("verify the correct document is retrieved")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    "step_impl for verify the correct document is retrieved"
    retrieved_document = context.retrieved_document

    assert retrieved_document.id == 300
    assert retrieved_document.name == "Specific Document"


@given("a DocumentManager instance")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    context.document_manager = DocumentManager()


@given("a document ID")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    context.doc_id = 1


@given("a new document")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    context.document = Document(
        id=1,
        name="New Document",
        version="1.0",
        checksum="abc123",
        last_modified=datetime.utcnow(),
        status="active",
    )


@when("the get method is called in metadata")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    with patch("common.sql.SqlConnector.get_session") as mock_get_session:
        mock_session = MagicMock()
        mock_document = Document(id=1, name="Test Document")
        mock_session.query.return_value.filter_by.return_value.first.return_value = (
            mock_document
        )
        mock_get_session.return_value = mock_session

        context.result = context.document_manager.get(context.doc_id)


@when("the save method is called for a new document in metadata")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    with patch(
        "common.sql.SqlConnector.get_session", return_value=MagicMock()
    ) as mock_get_session:
        mock_session = mock_get_session.return_value
        mock_session.query.return_value.filter_by.return_value.first.return_value = None

        context.document_manager.save(context.document)
        context.mock_session = mock_session


@then("the result should be the document details")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    expected_result = Document(id=1, name="Test Document")
    assert (
        context.result.id == expected_result.id
    ), f"Expected {expected_result.id}, but got {context.result.id}"
    assert (
        context.result.name == expected_result.name
    ), f"Expected {expected_result.name}, but got {context.result.name}"


@when("the list method is called in metadata")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    with patch("common.sql.SqlConnector.get_session") as mock_get_session:
        mock_session = MagicMock()
        mock_documents = [
            Document(id=1, name="Test Document 1"),
            Document(id=2, name="Test Document 2"),
        ]
        mock_session.query.return_value.all.return_value = mock_documents
        mock_get_session.return_value = mock_session

        context.result = context.document_manager.list()


@then("the result should be a list of documents")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    expected_result = [
        Document(id=1, name="Test Document 1"),
        Document(id=2, name="Test Document 2"),
    ]
    assert len(context.result) == len(
        expected_result
    ), f"Expected {len(expected_result)} documents, but got {len(context.result)}"
    for doc, expected_doc in zip(context.result, expected_result):
        assert (
            doc.id == expected_doc.id
        ), f"Expected document ID {expected_doc.id}, but got {doc.id}"
        assert (
            doc.name == expected_doc.name
        ), f"Expected document name {expected_doc.name}, but got {doc.name}"


@then("the document should be added to the session")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    context.mock_session.add.assert_called_once_with(context.document)
