"""Module to handle returning appropriate encoding for request data"""

from typing import Protocol
from abc import abstractmethod

import compression.gzip as gz


class ContentEncoder(Protocol):
    @abstractmethod
    def encode_data(self, b: bytes) -> bytes:
        raise NotImplementedError

class GzipEncoder:
    def encode_data(self, b: bytes) -> bytes:
        return gz.compress(b)

# TODO: This is basic but don't think it needs to be anything more, could maybe update to be an Enum
def get_encoder_func(e: str) -> ContentEncoder | None:
    if e == "gzip":
        return GzipEncoder()

    return None
