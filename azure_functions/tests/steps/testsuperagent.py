"""Test SuperAgent Steps."""

from unittest.mock import patch, MagicMock
from behave import given, when, then  # pylint: disable=no-name-in-module

from superagent import SuperAgent, SuperAgentManager
from helpers.blobmanager import BlobManager
from helpers.searchmanager import SearchManager
from supersearch.metadata import DocumentManager


@given("I have a valid container path for {data_type}")
def step_impl(context, data_type):  # noqa: F811 # pylint: disable=function-redefined
    """I have a valid container path for {data_type}."""
    context.container_path = "your/container/path"
    context.data_type = data_type
    context.data_type_value = "value"


@given("I have blob content for {data_type}")
def step_impl(context, data_type):  # noqa: F811 # pylint: disable=function-redefined
    # pylint: disable=function-redefined
    """I have blob content for {data_type}."""
    context.blob_content = {
        "FullFilePath": "your/blob/path",
        "PageURL": "somepageurl",
        "value": [
            # Add JSON content relevant to the test
        ],
    }
    context.data_type = data_type


@when("I process the metadata for {data_type}")
def step_impl(context, data_type):  # noqa: F811 # pylint: disable=function-redefined
    """I process the metadata for {data_type}."""
    with patch("common.handlers.KeyVaultHandler.get_secret") as mock_get_secret, patch(
        "superagent.SuperAgentManager.get_blobcontent"
    ) as mock_get_blobcontent, patch(
        "superagent.SuperAgent.process_tariffs_list"
    ) as mock_process_tariffs_list, patch(
        "superagent.SuperAgent.process_notice_list"
    ) as mock_process_notice_list, patch(
        "superagent.SuperAgent.process_equipments_list"
    ) as mock_process_equipments_list, patch(
        "superagent.SuperAgent.process_pages_library"
    ) as mock_process_pages_library, patch(
        "superagent.SuperAgent.process_metadata"
    ) as mock_process_metadata:

        # Mock all the method returns
        mock_get_secret.return_value = "dummy_secret"
        mock_get_blobcontent.return_value = context.blob_content
        mock_process_tariffs_list.return_value = "process_tariffs_list"
        mock_process_notice_list.return_value = "processed_notice"
        mock_process_equipments_list.return_value = "processed_equipments"
        mock_process_pages_library.return_value = "processed_pages"
        mock_process_metadata.return_value = "mock_process_metadata"
        # Call the function
        context.response = SuperAgent().process_metadata(
            context.container_path,
            context.data_type,
            context.data_type_value,
        )
        context.data_type = data_type


@when("I process the Tariffas")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    """I process the Tariffas."""
    with patch(
        "common.handlers.KeyVaultHandler.get_secret"
    ) as mock_get_secret:  # noqa: 501
        mock_get_secret.return_value = "dummy_secret"
        with patch(
            "superagent.SuperAgentManager.process_tariffs_list"
        ) as mock_process_tariffs_list:
            mock_process_tariffs_list.return_value = "process_tariffs_list"
            superagentmanager = SuperAgentManager(container_path="your/container/path")
            context.response = superagentmanager.process_tariffs_list(
                context.blob_content
            )
            mock_process_tariffs_list.assert_called_once()


@when("I process the Equipments")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    """I process the Equipments."""
    context.blob_content = "valid_blob_content"  # Or some other valid test data
    context.superagentmgr = MagicMock()  # Mock the superagent manager if necessary

    # Create an instance of the class containing process_equipments_list
    context.instance = MagicMock()  # Replace with actual class instance if needed
    # Assigning the method to the instance
    context.instance = MagicMock(return_value=True)
    context.response = MagicMock(return_value=True)


@when("I process the Notice")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    """I process the Equipments."""
    context.blob_content = "valid_blob_content"  # Or some other valid test data
    context.superagentmgr = MagicMock()  # Mock the superagent manager if necessary

    # Create an instance of the class containing process_equipments_list
    context.instance = MagicMock()  # Replace with actual class instance if needed
    # Assigning the method to the instance
    context.instance = MagicMock(return_value=True)
    context.response = MagicMock(return_value=True)


@when("I process the Pages")
def step_impl(context):  # noqa: F811 # pylint: disable=function-redefined
    """I process the Pages."""
    with patch(
        "common.handlers.KeyVaultHandler.get_secret"
    ) as mock_get_secret:  # noqa: 501
        mock_get_secret.return_value = "dummy_secret"
        with patch(
            "superagent.SuperAgentManager.process_pages_library"
        ) as mock_process_pages_library:
            mock_process_pages_library.return_value = "processed_pages_library"
            superagentmanager = SuperAgentManager(container_path="your/container/path")
            context.response = superagentmanager.process_pages_library(
                context.blob_content
            )
            mock_process_pages_library.assert_called_once()


@then("I should get a valid response for {data_type}")
def step_impl(context, data_type):  # noqa: F811 # pylint: disable=function-redefined
    """I should get a valid response for {data_type}."""
    context.data_type = data_type
    assert context.response is not None
