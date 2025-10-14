"""Container path for the document for all the API methods calls parameter

    Returns:
        _type_: return the container path
"""

import azure.functions as func


class ContainerPath:
    """
    Represents a container path
    """

    def __init__(
        self,
        req: func.HttpRequest,
    ):
        self.req = req

    def get_container_path(self):
        "Getting the container path via body or parameters though get"
        container_path = self.req.params.get("containerFilePath")
        if not container_path:
            try:
                req_body = self.req.get_json()
                container_path = req_body.get("containerFilePath")
            except ValueError:
                return False
        return container_path
