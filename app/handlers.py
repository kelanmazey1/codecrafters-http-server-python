"""All handlers for a given path and request type"""

from typing import Any
from app.messages import (
    HTTPRequestMethod,
    HTTPResponse,
    HTTPBody,
    HTTPHeaders,
    HTTPRequest,
    get_bad_400_resp,
    get_not_found_404_resp,
    get_ok_200_resp,
)
import app.router as router
from app.directory import get_file_tree


r = router.get_router()
file_tree = get_file_tree()

@r.register("/", HTTPRequestMethod.GET)
def handle_root(params: dict[str, Any], req: HTTPRequest) -> HTTPResponse:
    return get_ok_200_resp()

@r.register("/files/{file_name}", HTTPRequestMethod.GET)
def handle_files(params: dict[str, Any], req: HTTPRequest) -> HTTPResponse:

    root = file_tree.get_root()
    print("in the file handler")
    file_name = params["file_name"]

    file_path = root / file_name
    print(file_path)

    if file_path.exists():
        with open(file_path, "rb") as file:
            f = file.read()

        return get_ok_200_resp(
            h=HTTPHeaders({
                "Content-Type": "application/octet-stream",
                "Content-Length": len(f),
            }),
            b=HTTPBody(f)
        )
    else:
        return get_not_found_404_resp()

@r.register("/echo/{message}", HTTPRequestMethod.GET)
def handle_echo(params: dict[str, Any], req: HTTPRequest) -> HTTPResponse:
    payload = params["message"]

    return get_ok_200_resp(
        HTTPHeaders(
            {
                "Content-Type": "text/plain",
                "Content-Length": len(payload),
            }
        ),
        HTTPBody(payload),
    )


@r.register("/user-agent", HTTPRequestMethod.GET)
def handle_user_agent(params: dict[str, Any], req: HTTPRequest) -> HTTPResponse:

    if req.headers:
        user_agent = req.headers.get_header("User-Agent")

        if not user_agent:
            return get_bad_400_resp()

        return get_ok_200_resp(
            HTTPHeaders(
                {
                    "Content-Type": "text/plain",
                    "Content-Length": len(user_agent),
                }
            ),
            HTTPBody(user_agent),
        )

    else:
        return get_bad_400_resp()
