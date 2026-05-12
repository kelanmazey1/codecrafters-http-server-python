"""All handlers for a given path and request type"""

from typing import Any, Protocol
from app.messages import (
    HTTPRequestMethod,
    HTTPResponse,
    HTTPResponseLine,
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

# TODO: mypy reocgnises that  decorated funcs are HTTPHandlers but doesn't error when you register foo() -> None:
# Think it is just strictness but worth a play
class HTTPHandler(Protocol):
    """Defining protocol for signature, handler(params: dict[str, Any], req: HTTPRequest) -> HTTPResponse
    This is probably overkill but wanted to use it"""
    def __call__(self, params: dict[str, Any], req: HTTPRequest) -> HTTPResponse:
        """Use call here so function can satisfy protocol"""
        ...


@r.register("/", HTTPRequestMethod.GET)
def handle_root(params: dict[str, Any], req: HTTPRequest) -> HTTPResponse:
    return get_ok_200_resp()

@r.register("/files/{file_name}", HTTPRequestMethod.GET)
def get_files(params: dict[str, Any], req: HTTPRequest) -> HTTPResponse:

    root = file_tree.get_root()
    file_name = params["file_name"]

    file_path = root / file_name

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

@r.register("/files/{file_name}", HTTPRequestMethod.POST)
def make_files(params: dict[str, Any], req: HTTPRequest) -> HTTPResponse:

    root = file_tree.get_root()
    file_name = params["file_name"]

    if not req.body:
        return get_bad_400_resp()

    file_path = root / file_name

    file_path.touch(exist_ok=True)

    with open(file_path, "wb") as file:
        file.write(req.body.to_bytes())

    return HTTPResponse(
        response_line=HTTPResponseLine(code=201, reason_phrase="Created"),
    )

@r.register("/echo/{message}", HTTPRequestMethod.GET)
def handle_echo(params: dict[str, Any], req: HTTPRequest) -> HTTPResponse:
    payload = params["message"]

    # Each handler decides what encodings (or other headers ie. Content-Type) it accepts
    resp_encoding = req.headers.validate_field(valid_encoding = (
        "gzip",
    ), field_name="Accept-Encoding")


    resp_headers = HTTPHeaders(
            {
                "Content-Type": "text/plain",
                "Content-Length": len(payload),
            }
        )

    if resp_encoding:
        resp_headers.set_header("Content-Encoding", resp_encoding)

    return get_ok_200_resp(
        resp_headers,
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
