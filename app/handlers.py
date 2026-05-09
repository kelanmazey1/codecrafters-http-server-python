"""All handlers for a given path and request type"""

from app.messages import (
    HTTPRequestMethod,
    HTTPResponse,
    HTTPResponseLine,
    HTTPBody,
    HTTPHeaders,
)
import app.router as router


r = router.get_router()


@r.register("/", HTTPRequestMethod.GET)
def handle_root(params) -> HTTPResponse:
    return HTTPResponse(response_line=HTTPResponseLine(code=200, reason_phrase="OK"))


@r.register("/echo/{message}", HTTPRequestMethod.GET)
def handle_echo(params) -> HTTPResponse:
    payload = params["message"]

    return HTTPResponse(
        response_line=HTTPResponseLine(code=200, reason_phrase="OK"),
        headers=HTTPHeaders(
            {
                "Content-Type": "text/plain",
                "Content-Length": len(payload),
            }
        ),
        body=HTTPBody(payload),
    )
