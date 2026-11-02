"""EOS (Antelope) adapter. Read-only: it uses the chain API and signs nothing."""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

import requests

from ..errors import NetworkError, NotFoundError
from ..models import CONFIRMED, Asset, Balance, Receipt, Wallet
from .base import Chain, NetworkConfig

ACCOUNT_NAME = re.compile(r"^[a-z1-5.]{0,11}[a-z1-5]$")
TOKEN_CONTRACT = "eosio.token"  # noqa: S105
TIMEOUT_SECONDS = 20
WRITE_MESSAGE = (
    "EOS support is read-only. Signing needs ABI-aware Antelope serialization that this library "
    "does not include."
)


class EosChain(Chain):
    """An EOS address is an account name of up to 12 characters. An existing account creates it."""

    name = "eos"
    native = Asset("EOS", None)
    default_network = "jungle4"
    networks = {
        "mainnet": NetworkConfig("https://eos.greymass.com", mainnet=True),
        "jungle4": NetworkConfig("https://jungle4.greymass.com"),
    }

    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        try:
            response = requests.post(f"{self.url}{path}", json=payload, timeout=TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            raise NetworkError(f"{path} failed: {exc}") from exc
        if response.status_code in (400, 404, 500):
            error = response.json().get("error", {}) if response.content else {}
            missing = ("unknown_transaction_exception", "account_query_exception")
            if error.get("name") in missing or response.status_code == 404:
                raise NotFoundError(f"{path}: {error.get('what', 'not found')}")
            raise NetworkError(f"{path} returned {response.status_code}: {error.get('what')}")
        if not response.ok:
            raise NetworkError(f"{path} returned {response.status_code}")
        return response.json()

    def create_wallet(self) -> Wallet:
        raise self._unsupported("creating wallets, since an existing account must create one")

    def wallet_from_secret(self, secret: str) -> Wallet:
        raise self._unsupported(WRITE_MESSAGE)

    def is_valid_address(self, address: str) -> bool:
        return bool(ACCOUNT_NAME.match(address))

    def info(self) -> dict[str, Any]:
        """Return the chain's head block and identity."""
        return self._post("/v1/chain/get_info", {})

    def account(self, name: str) -> dict[str, Any]:
        """Return an account's resources and permissions."""
        self._require_address(name)
        return self._post("/v1/chain/get_account", {"account_name": name})

    def balances(self, address: str) -> list[Balance]:
        self._require_address(address)
        rows = self._post(
            "/v1/chain/get_currency_balance",
            {"code": TOKEN_CONTRACT, "account": address, "symbol": self.native.code},
        )
        if not rows:
            return [Balance(self.native, Decimal(0))]
        amount, _, _symbol = rows[0].partition(" ")
        return [Balance(self.native, Decimal(amount))]

    def transfer(
        self,
        wallet: Wallet,
        to: str,
        amount: Decimal | str | int,
        *,
        asset: Asset | None = None,
        reference: str | None = None,
        wait: bool = True,
    ) -> Receipt:
        raise self._unsupported(WRITE_MESSAGE)

    def transaction(self, tx_id: str) -> Receipt:
        record = self._post("/v1/history/get_transaction", {"id": tx_id})
        return Receipt(self.name, self.network, tx_id, CONFIRMED, record)
