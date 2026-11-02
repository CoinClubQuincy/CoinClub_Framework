"""Client for the Xaman (formerly XUMM) platform API.

Xaman users approve XRPL transactions in their own wallet app, so your server never holds their
keys. Create API credentials in the Xaman developer console.
"""

from __future__ import annotations

from typing import Any

import requests

from .errors import NetworkError, NotFoundError, ValidationError

BASE_URL = "https://xumm.app/api/v1/platform"
TIMEOUT_SECONDS = 20


class XamanClient:
    def __init__(self, api_key: str, api_secret: str, *, base_url: str = BASE_URL):
        if not api_key or not api_secret:
            raise ValidationError("Xaman needs both an API key and an API secret")
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update(
            {"X-API-Key": api_key, "X-API-Secret": api_secret, "Accept": "application/json"}
        )

    def __repr__(self) -> str:
        return "<XamanClient>"

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        try:
            response = self._session.request(
                method, f"{self._base_url}/{path}", json=body, timeout=TIMEOUT_SECONDS
            )
        except requests.RequestException as exc:
            # The exception is not chained to the session, so headers stay out of tracebacks.
            raise NetworkError(f"Xaman {path} failed: {type(exc).__name__}") from None
        if response.status_code == 404:
            raise NotFoundError(f"Xaman {path}: not found")
        if not response.ok:
            raise NetworkError(f"Xaman {path} returned {response.status_code}: {response.text}")
        return response.json()

    def ping(self) -> dict[str, Any]:
        """Check the credentials and return the application's details."""
        return self._request("GET", "ping")

    def create_payload(
        self,
        txjson: dict[str, Any],
        *,
        submit: bool = True,
        multisign: bool = False,
        expire_minutes: int | None = None,
        custom_id: str | None = None,
        user_token: str | None = None,
        instruction: str | None = None,
    ) -> dict[str, Any]:
        """Ask a user to sign a transaction. The result holds a QR code and a sign link."""
        options: dict[str, Any] = {"submit": submit, "multisign": multisign}
        if expire_minutes is not None:
            options["expire"] = expire_minutes
        body: dict[str, Any] = {"txjson": txjson, "options": options}
        meta: dict[str, str] = {}
        if custom_id is not None:
            meta["identifier"] = custom_id
        if instruction is not None:
            meta["instruction"] = instruction
        if meta:
            body["custom_meta"] = meta
        if user_token is not None:
            body["user_token"] = user_token
        return self._request("POST", "payload", body)

    def get_payload(self, uuid: str) -> dict[str, Any]:
        return self._request("GET", f"payload/{uuid}")

    def get_payload_by_custom_id(self, custom_id: str) -> dict[str, Any]:
        return self._request("GET", f"payload/ci/{custom_id}")

    def cancel_payload(self, uuid: str) -> dict[str, Any]:
        return self._request("DELETE", f"payload/{uuid}")

    def curated_assets(self) -> dict[str, Any]:
        return self._request("GET", "curated-assets")

    def kyc_status(self, account: str) -> dict[str, Any]:
        return self._request("GET", f"kyc-status/{account}")

    def transaction(self, tx_hash: str) -> dict[str, Any]:
        return self._request("GET", f"xrpl-tx/{tx_hash}")

    def rates(self, currency: str) -> dict[str, Any]:
        return self._request("GET", f"rates/{currency}")

    def push(
        self, user_token: str, body: str, *, subtitle: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a push notification to a user who has signed in to your xApp."""
        return self._request(
            "POST", "xapp/push", self._notification(user_token, body, subtitle, data)
        )

    def event(
        self, user_token: str, body: str, *, subtitle: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a push notification that is also listed in the user's event list."""
        return self._request(
            "POST", "xapp/event", self._notification(user_token, body, subtitle, data)
        )

    @staticmethod
    def _notification(
        user_token: str, body: str, subtitle: str | None, data: dict[str, Any] | None
    ) -> dict[str, Any]:
        message: dict[str, Any] = {"user_token": user_token, "body": body}
        if subtitle is not None:
            message["subtitle"] = subtitle
        if data is not None:
            message["data"] = data
        return message
