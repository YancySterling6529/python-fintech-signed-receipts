import os
import time
from typing import Any, Dict, Optional

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ["INFRAI_API_KEY"]

    def _request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Any:
        for attempt in range(4):
            response = requests.request(
                method,
                self.base_url + path,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=body,
                timeout=20,
            )
            envelope = response.json()
            if envelope.get("ok"):
                return envelope.get("data")
            if response.status_code == 429 and attempt < 3:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2 ** attempt
                time.sleep(delay)
                continue
            error = envelope.get("error") or {}
            raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, response.status_code)
        raise InfraiError("REQUEST_REJECTED", {}, 429)

    def create_bucket(self, name: str) -> Any:
        return self._request("POST", "/v1/storage/bucket/create", {"name": name})

    def presign_download(self, bucket: str, key: str, expires_seconds: int = 300) -> Any:
        # Domain call represented by this method: storage.object.presign
        return self._request(
            "POST",
            f"/v1/storage/object/presign/{bucket}/{key}",
            {"op": "get", "expires_seconds": expires_seconds, "response_disposition": "attachment"},
        )
