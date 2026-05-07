from enum import Enum, auto
from pathlib import Path
from abc import ABC, abstractmethod

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

    def get_request_type(self) -> HTTPRequestMethod:
        if self.status_line[:3] == "GET":
            return HTTPRequestMethod.GET
        elif self.status_line[:3] == "PUT":
            return HTTPRequestMethod.PUT
        elif self.status_line[:4] == "POST":
            return HTTPRequestMethod.POST
        else:
            raise ValueError(
                f"Could not establish request type from status line: {self.status_line.decode("utf-8")}"
            )

    def get_path(self) -> Path:
        str_parts = self.status_line.decode("utf-8").split(sep=" ")
        return Path(str_parts[1])


class HTTPResponseLine:
    def __init__(self, code: int, reason_phrase: None | str = None):
        self.protocol = PROTOCOL
        self.code = code
        self.reason_phrase = reason_phrase

    def __str__(self):
        return f"{self.protocol} {self.code} {self.reason_phrase}\r\n"

    def as_bytes(self):
        return str(self).encode(encoding="utf-8")


class HTTPHeaders:
    def __init__(self, headers: bytes):
        pass


class HTTPBody:
    def __init__(self, body: bytes):
        pass


class HTTPResponse:
    def __init__(
        self, response_line: HTTPResponseLine, headers: HTTPHeaders | None = None, body: HTTPBody | None = None
    ) -> None:
        self.response_line = response_line
        self.headers = headers
        self.body = body

    def get_response_line_bytes(self) -> bytes:
        """Return self.response_line decoded to utf-8"""
        return self.response_line.as_bytes()
    
               


class HTTPRequest:
    def __init__(
        self, status_line: HTTPStatusLine, headers: HTTPHeaders | None = None, body: HTTPBody | None = None
    ) -> None:
        self.status_line = status_line
        self.headers = headers
        self.body = body

    @classmethod
    def from_tcp(cls, data: bytes) -> HTTPRequest:
        lines = data.split(b"\r\n")

        if lines[-1] != b"":
            raise ValueError("Input did not end with \\r\\n")

        lines = lines[:len(lines)] # Remove all but last as this should always be ""
        status_line = HTTPStatusLine(lines[0])
        headers = None if len(lines) < 2 else HTTPHeaders(lines[1])
        body = None if len(lines) < 3 else HTTPBody(lines[2])

        return cls(status_line, headers, body)
    
    def get_path(self) -> Path:
        return self.status_line.get_path()

    def get_request_type(self) -> HTTPRequestMethod:
        return self.status_line.get_request_type()
