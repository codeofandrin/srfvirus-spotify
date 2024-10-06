from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from requests import Response


class SRFHTTPException(BaseException):

    def __init__(self, response: Response, data: Dict[str, Any]):
        self.response: Response = response

        self.reason: Optional[str] = self.response.reason
        self.data: Dict[str, Any] = data

        super().__init__(f"{self.data}")
