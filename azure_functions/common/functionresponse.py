"Function response with JSON"
import json
import azure.functions as func


class FunctionResponse:
    """
    Represents a function response with JSON
    """

    @classmethod
    def return_http_response(
        cls,
        message,
        status_code,
    ):
        "HTTP response sent out to API method caller"
        return func.HttpResponse(
            json.dumps(
                {
                    "Code": status_code,
                    "Message": message,
                }
            ),
            status_code=status_code,
            headers={"Content-Type": "application/json"},
        )
