"""All handlers for a given path and request type"""

from typing import Any, Callable
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
from app.encoding import get_encoder_func


r = router.get_router()
file_tree = get_file_tree()


def get_encoding(e: str) -> Callable | None:
    """Returns callable which can encode bytes."""


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
            h=HTTPHeaders(
                {
                    "Content-Type": "application/octet-stream",
                    "Content-Length": len(f),
                }
            ),
            b=HTTPBody(f),
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

    if not req.headers:
        return get_bad_400_resp()

    resp_headers = HTTPHeaders(
        {
            "Content-Type": "text/plain",
        }
    )

    encoding_specified = req.headers.get_header("Accept-Encoding")
    encoding_applied = False
    if encoding_specified:
        # Could be multiple codings specified
        for encoding in encoding_specified.split(","):
            encoder = get_encoder_func(
                encoding.strip()
            )  # Valid encodings handled in separate module
            if encoder:
                body = HTTPBody(encoder.encode_data(payload.encode("utf-8")))
                resp_headers.set_header("Content-Encoding", encoding)
                encoding_applied = True
                break

    if not encoding_applied:
        body = HTTPBody(payload)

    resp_headers.set_header("Content-Length", len(body))

    return get_ok_200_resp(
        resp_headers,
        body,
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


@r.register("/hi/{name}", HTTPRequestMethod.GET)
def show_fancy_name(params: dict[str, Any], req: HTTPRequest) -> HTTPResponse:
    body = HTTPBody(f"""<!DOCTYPE html>
    <html>
    <head>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Segoe UI', sans-serif;
        }}
        .card {{
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 20px;
        padding: 60px 80px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }}
        h1 {{
        color: white;
        font-size: 3rem;
        font-weight: 300;
        letter-spacing: 2px;
        }}
        h1 span {{
        font-weight: 700;
        background: linear-gradient(90deg, #f9d423, #ff4e50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        }}
    </style>
    </head>
    <body>
    <div class="card">
        <h1>Hi, <span>{params["name"]}</span>!</h1>
    </div>
    </body>
    </html>""")
    return get_ok_200_resp(
        h=HTTPHeaders({"Content-Type": "text/html", "Content-Length": len(body)}),
        b=body,
    )
