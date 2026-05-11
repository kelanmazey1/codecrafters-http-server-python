from enum import Enum, auto
from typing import Any

PROTOCOL = "HTTP/1.1"


class HTTPRequestMethod(Enum):
    GET = auto()
    POST = auto()
    PUT = auto()


class HTTPStatusLine:
    def __init__(self, status_line: bytes):
        self.status_line = status_line

    def __str__(self):
        return self.status_line

    def __repr__(self):
        return f"HTTPStatusLine(status_line={self.status_line!r})"

    def get_request_type(self) -> HTTPRequestMethod:
        if self.status_line[:3] == b"GET":
            return HTTPRequestMethod.GET
        elif self.status_line[:3] == b"PUT":
            return HTTPRequestMethod.PUT
        elif self.status_line[:4] == b"POST":
            return HTTPRequestMethod.POST
        else:
            raise ValueError(
                f"Could not establish request type from status line: {self.status_line.decode('utf-8')}"
            )

    def get_path(self) -> str:
        """Get's path from self.status_line will always return index.html -> /index.html"""
        str_parts = self.status_line.decode("utf-8").split(sep=" ")
        return "/" + str_parts[1].strip("/")


class HTTPResponseLine:
    def __init__(self, code: int, reason_phrase: None | str = None):
        self.protocol = PROTOCOL
        self.code = code
        self.reason_phrase = reason_phrase

    def __str__(self):
        return f"{self.protocol} {self.code} {self.reason_phrase}\r\n"

    def __repr__(self):
        return f"HTTPResponseLine(code={self.code!r}, reason_phrase={self.reason_phrase!r})"

    def to_bytes(self, encoding="utf-8"):
        return str(self).encode(encoding)


class HTTPHeaders:
    def __init__(self, headers: dict[str, Any]):
        self.headers = headers

    def __repr__(self):
        return f"HTTPHeaders(headers={self.headers!r})"

    @classmethod
    def from_bytes(cls, data: bytes) -> HTTPHeaders:
        lines = data.split(b"\r\n")  # Get lines field:value
        out = {}
        
        for pair in lines:
            field_val = pair.split(b":", 1)  # Get list ["field", "value"]

            if len(field_val) != 2:
                raise ValueError(
                    f"Split headers didn't result in only field and value: {[v for v in field_val]}"
                )

            
            field = field_val[0].decode("utf-8").strip()
            val = field_val[1].decode(
                "utf-8"
            ).strip()  # Add as {"field": "value"}, always returns as a string

            out[field] = val

        return cls(out)

    def to_bytes(self, encoding="utf-8") -> bytes:
        out = bytearray()
        for field, val in self.headers.items():
            line = f"{field}: {val}\r\n"
            out.extend(line.encode(encoding))

        out.extend(b"\r\n")  # Final CRLF to know headers are over
        return out
    
    def get_header(self, field: str) -> str | None:
        return self.headers.get(field)


class HTTPBody:
    def __init__(self, body: str | bytes):
        self.body = body

    def __repr__(self):
        return f"HTTPBody(body={self.body!r})"

    def to_bytes(self, encoding="utf-8") -> bytes:
        """Return self.body as bytes with encoding"""
        if isinstance(self.body, str ):
            return self.body.encode(encoding)
        return self.body


class HTTPResponse:
    def __init__(
        self,
        response_line: HTTPResponseLine,
        headers: HTTPHeaders | None = None,
        body: HTTPBody | None = None,
    ) -> None:
        self.response_line = response_line
        self.headers = headers
        self.body = body

    def __repr__(self):
        return f"HTTPResponse(response_line={self.response_line!r}, headers={self.headers!r}, body={self.body!r})"

    def get_response_line_bytes(self) -> bytes:
        """Return self.response_line decoded to utf-8"""
        return self.response_line.to_bytes()

    def to_bytes(self, encoding="utf-8") -> bytes:
        """Return self as bytes, for sending back across TCP"""
        out = bytearray()
        out.extend(self.response_line.to_bytes(encoding))

        if self.headers:
            out.extend(self.headers.to_bytes(encoding))

        if self.body:
            out.extend(self.body.to_bytes(encoding))

        return out


class HTTPRequest:
    def __init__(
        self,
        status_line: HTTPStatusLine,
        headers: HTTPHeaders | None = None,
        body: HTTPBody | None = None,
    ) -> None:
        self.status_line = status_line
        self.headers = headers
        self.body = body

    def __repr__(self):
        return f"HTTPRequest(status_line={self.status_line!r}, headers={self.headers!r}, body={self.body!r})"

    @classmethod
    def from_bytes(cls, data: bytes) -> HTTPRequest:
        first_line, _, head_body = data.partition(b"\r\n")
        stat_line = HTTPStatusLine(first_line)

        # if no head or body
        if head_body == b"\r\n":
            return cls(stat_line)

        headers_block, _, body_block = head_body.partition(b"\r\n\r\n")
        
        return cls(stat_line, HTTPHeaders.from_bytes(headers_block), HTTPBody(body_block))

    def get_path(self) -> str:
        return self.status_line.get_path()

    def get_request_type(self) -> HTTPRequestMethod:
        return self.status_line.get_request_type()


def get_ok_200_resp(h: HTTPHeaders | None = None, b: HTTPBody | None = None) -> HTTPResponse:
    return  HTTPResponse(response_line=HTTPResponseLine(code=200, reason_phrase="OK"), headers=h, body=b)

def get_not_found_404_resp(h: HTTPHeaders | None = None, b: HTTPBody | None = None) -> HTTPResponse:
    return  HTTPResponse(response_line=HTTPResponseLine(code=404, reason_phrase="Not Found"), headers=h, body=b)

def get_bad_400_resp(h: HTTPHeaders | None = None, b: HTTPBody | None = None) -> HTTPResponse:
    return HTTPResponse(response_line=HTTPResponseLine(code=400, reason_phrase="Bad Request"), headers=h, body=b)
