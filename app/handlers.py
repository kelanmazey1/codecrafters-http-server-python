"""All handlers for a given path and request type"""

from typing import Any
from app.messages import (
    HTTPRequestMethod,
    HTTPResponse,
    HTTPBody,
    HTTPHeaders,
    HTTPRequest,
    get_bad_400_resp,
    get_ok_200_resp,
)
import app.router as router


r = router.get_router()


@r.register("/", HTTPRequestMethod.GET)
def handle_root(params: dict[str, Any], req: HTTPRequest) -> HTTPResponse:
    return get_ok_200_resp()


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
