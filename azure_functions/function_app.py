"""Function app to process metadata and delete index.

Raises:
    e: raise exception when failed to run supersearch or superagent methods

Returns:
        type_: return the results based on API request
"""

import logging
import os
import json
from datetime import datetime

import azure.functions as func
from common.containerpath import ContainerPath
from common.functionresponse import FunctionResponse

from supersearch import SuperSearch

logger = logging.getLogger("azure")
logger.setLevel(logging.ERROR)

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


# # Heartbeat service to check Azure Function health and build number
# @app.route(route="heartbeat", methods=["GET"])
# def heartbeat(req: func.HttpRequest) -> func.HttpResponse:
#     """Heartbeat service to check Azure Function health and build number."""
#     _build_id = os.environ["BUILD_ID"]
#     if _build_id is None:
#         _build_id = "Local Build"
#     logging.info(
#         "Build id %s: Heartbeat request received @%s. Time is in UTC.",
#         _build_id,
#         datetime.utcnow(),
#     )
#     return func.HttpResponse(
#         f"Build id {_build_id}: Function is alive @ {datetime.utcnow()}."  # noqa 501
#         f"Time is in UTC",
#         status_code=200,
#     )


@app.function_name(name="superagent")
@app.timer_trigger(
    schedule="0 */15 * * * *",
    arg_name="superagentimer",
    run_on_startup=False,
)
def superagent(superagentimer: func.TimerRequest) -> None:
    # Get the request body
    _build_id = os.getenv("BUILD_ID", "Local Build")
    utc_timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    if superagentimer.past_due:
        logger.info("The timer is past due for build id %s!", _build_id)
    logger.info(
        "Python timer trigger function ran at %s for build id %s",
        utc_timestamp,
        _build_id,
    )
    try:
        logger.info(
            "Importing super agent for build id %s",
            _build_id,
        )

        # Create an instance of the SuperAgent class
        from superagent import SuperAgent

        _superagent = SuperAgent()
        _config_name = os.getenv(
            "SUPERAGENT_CONFIG_NAME",
            "superagent.yaml",
        )
        logger.info(
            "SuperAgent object created for build id %s",
            _build_id,
        )
        _response = _superagent.extract(
            config_name=_config_name,
        )
        if _response:
            logger.info(
                "Document has been successfully processed and moved. Status code=200"
            )
        else:
            logger.info("Document has not been processed. Status code=404")

        logger.info(
            "SuperAgent run completed for build id %s",
            _build_id,
        )
    except Exception as e:
        logger.error("Failed to run superagent", exc_info=e)
        raise e


# @app.route(route="getMetadata", methods=["GET", "POST"])
# def getmetadata(req: func.HttpRequest) -> func.HttpResponse:
#     """Get metadata from the container path."""
#     # Set global TracerProvider before instrumenting
#     container_path = ContainerPath(req).get_container_path()
#     data_type = req.params.get("datatype")
#     data_type_value = req.params.get("datatypevalue")
#     if container_path and data_type and data_type_value:
#         try:
#             _orchestrator = SuperAgent()
#             _response = _orchestrator.process_metadata(
#                 container_path,
#                 data_type,
#                 data_type_value,
#             )
#             if _response:
#                 return FunctionResponse.return_http_response(
#                     "Document has been successfully processed", status_code=200
#                 )
#             else:
#                 return FunctionResponse.return_http_response(
#                     "Document has not been processed, existed in the Index",
#                     status_code=200,
#                 )
#         except ValueError:
#             return FunctionResponse.return_http_response(
#                 "Document has not been processed", status_code=403
#             )
#     else:
#         return FunctionResponse.return_http_response(
#             "No document found for the provided input field.", status_code=404
#         )


# @app.route(route="deleteIndex", methods=["GET", "POST"])
# def deleteindex(req: func.HttpRequest) -> func.HttpResponse:
#     """Delete index from the container path.

#     Args:
#         req (func.HttpRequest): Request object

#     Returns:
#         func.HttpResponse: Response object
#     """
#     # Set global TracerProvider before instrumenting
#     container_path = ContainerPath(req).get_container_path()

#     if container_path:
#         try:
#             _orchestrator = SuperAgent()
#             _response = _orchestrator.process_delete_index(container_path)
#             if _response:
#                 return FunctionResponse.return_http_response(
#                     "Document has been successfully processed", status_code=200
#                 )
#             else:
#                 return FunctionResponse.return_http_response(
#                     "Document has not been processed, it is not available",
#                     status_code=200,
#                 )
#         except ValueError:
#             return FunctionResponse.return_http_response(
#                 "Document has not been processed", status_code=403
#             )
#     else:
#         return FunctionResponse.return_http_response(
#             "No document found for the provided input field.", status_code=404
#         )


# @app.function_name(name="supersearch")
# @app.timer_trigger(
#     schedule="%SUPERSEARCH_RUN_SCHEDULE%",
#     arg_name="supersearchtimer",
#     run_on_startup=False,
# )
# def supersearch(supersearchtimer: func.TimerRequest) -> None:
#     """Supersearch timer function to run every 4 hours.

#     Args:
#         supersearchtimer (func.TimerRequest): timer request

#     Raises:
#         e: raise exception when failed to run supersearch
#     """
#     utc_timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
#     if supersearchtimer.past_due:
#         logging.info("The timer is past due!")
#     logging.info(
#         "Python timer trigger function ran at %s",
#         utc_timestamp,
#     )
#     try:
#         _build_id = os.getenv("BUILD_ID", "Local Build")
#         logging.info(
#             "Importing super search for build id %s",
#             _build_id,
#         )
#         _supersearch = SuperSearch()
#         # create the index if it does not exist
#         # do this only once
#         # if you do this in the thread pool executor
#         # it will create concurrency issues
#         _supersearch.create_index()
#         logging.info(
#             "SuperSearch object created for build id %s",
#             _build_id,
#         )
#         _supersearch.run()
#         logging.info(
#             "SuperSearch run completed for build id %s",
#             _build_id,
#         )
#     except Exception as e:
#         logging.error("Failed to run supersearch", exc_info=e)
#         raise e
