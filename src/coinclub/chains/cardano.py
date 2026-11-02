"""Cardano adapter, built on PyCardano and Blockfrost."""

from __future__ import annotations

import os
import time
from decimal import Decimal
from typing import Any

from blockfrost import ApiError
from pycardano import (
    Address,
    AlonzoMetadata,
    AuxiliaryData,
    BlockFrostChainContext,
    Metadata,
    MultiAsset,
    PaymentSigningKey,
    PaymentVerificationKey,
    TransactionBuilder,
    TransactionOutput,
    Value,
    min_lovelace,
)
from pycardano import Network as CardanoNetwork

from ..errors import (
    CoinClubError,
    NetworkError,
    NotFoundError,
    TransactionFailedError,
    ValidationError,
)
from ..models import (
    CONFIRMED,
    FAILED,
    PENDING,
    Asset,
    Balance,
    Receipt,
    Wallet,
    to_positive,
)
from .base import Chain, NetworkConfig

ADA_DECIMALS = 6
CIP20_LABEL = 674
CIP20_CHUNK_BYTES = 64
CONFIRMATION_TIMEOUT_SECONDS = 300
CONFIRMATION_POLL_SECONDS = 10


def _lovelace(amount: Decimal) -> int:
    scaled = amount.scaleb(ADA_DECIMALS)
    if scaled != scaled.to_integral_value():
        raise ValidationError(f"amount has more than {ADA_DECIMALS} decimal places")
    return int(scaled)


def _chunks(text: str) -> list[str]:
    """Split text into CIP-20 chunks of at most 64 bytes without breaking a character."""
    chunks: list[str] = []
    current = ""
    for char in text:
        if len((current + char).encode()) > CIP20_CHUNK_BYTES:
            chunks.append(current)
            current = ""
        current += char
    return [*chunks, current] if current else chunks


class CardanoChain(Chain):
    """Reads and writes need a Blockfrost project ID, from api_key or BLOCKFROST_PROJECT_ID.

    Native tokens are Asset(<asset name as hex>, issuer=<policy ID as hex>). Amounts of native
    tokens are whole base units, because Cardano does not record their decimals on chain.
    """

    name = "cardano"
    native = Asset("ADA")
    default_network = "preprod"
    networks = {
        "mainnet": NetworkConfig("https://cardano-mainnet.blockfrost.io/api", mainnet=True),
        "preprod": NetworkConfig("https://cardano-preprod.blockfrost.io/api"),
        "preview": NetworkConfig("https://cardano-preview.blockfrost.io/api"),
    }

    def __init__(
        self,
        network: str | None = None,
        *,
        url: str | None = None,
        allow_mainnet: bool = False,
        api_key: str | None = None,
        context: Any = None,
    ):
        super().__init__(network, url=url, allow_mainnet=allow_mainnet)
        self.address_network = CardanoNetwork.MAINNET if self.is_mainnet else CardanoNetwork.TESTNET
        self._api_key = api_key or os.environ.get("BLOCKFROST_PROJECT_ID")
        self._context = context

    @property
    def context(self) -> Any:
        if self._context is None:
            if not self._api_key:
                raise CoinClubError(
                    "Cardano needs a Blockfrost project ID: pass api_key or set "
                    "BLOCKFROST_PROJECT_ID"
                )
            self._context = BlockFrostChainContext(
                self._api_key, network=self.address_network, base_url=self.url
            )
        return self._context

    # Wallets. The secret is the signing key as hex.

    def _address(self, signing_key: PaymentSigningKey) -> Address:
        verification = PaymentVerificationKey.from_signing_key(signing_key)
        return Address(verification.hash(), network=self.address_network)

    def create_wallet(self) -> Wallet:
        signing_key = PaymentSigningKey.generate()
        return Wallet(self.name, str(self._address(signing_key)), signing_key.payload.hex())

    def wallet_from_secret(self, secret: str) -> Wallet:
        return Wallet(self.name, str(self._address(self._signing_key(secret))), secret)

    @staticmethod
    def _signing_key(secret: str) -> PaymentSigningKey:
        try:
            payload = bytes.fromhex(secret)
        except ValueError:
            raise ValidationError("not a valid Cardano signing key") from None
        if len(payload) != 32:
            raise ValidationError("not a valid Cardano signing key")
        return PaymentSigningKey(payload)

    def is_valid_address(self, address: str) -> bool:
        try:
            return Address.from_primitive(address).network == self.address_network
        except Exception:
            return False

    # Reads

    def balances(self, address: str) -> list[Balance]:
        self._require_address(address)
        try:
            utxos = self.context.utxos(address)
        except ApiError as exc:
            raise NetworkError(str(exc)) from exc
        lovelace = 0
        tokens: dict[Asset, int] = {}
        for utxo in utxos:
            lovelace += utxo.output.amount.coin
            for policy, names in utxo.output.amount.multi_asset.items():
                for name, quantity in names.items():
                    token = Asset(name.payload.hex(), policy.payload.hex())
                    tokens[token] = tokens.get(token, 0) + quantity
        result = [Balance(self.native, Decimal(lovelace).scaleb(-ADA_DECIMALS))]
        result.extend(Balance(token, Decimal(quantity)) for token, quantity in tokens.items())
        return result

    def transaction(self, tx_id: str) -> Receipt:
        try:
            record = self.context.api.transaction(tx_id)
        except ApiError as exc:
            if exc.status_code == 404:
                raise NotFoundError(f"no transaction {tx_id}") from exc
            raise NetworkError(str(exc)) from exc
        status = CONFIRMED if getattr(record, "valid_contract", True) else FAILED
        return Receipt(self.name, self.network, tx_id, status, {"block": record.block})

    # Writes

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
        self._require_write()
        self._require_wallet(wallet)
        self._require_address(to)
        value = to_positive(amount)
        signing_key = self._signing_key(wallet.secret)
        sender = self._address(signing_key)
        builder = TransactionBuilder(self.context)
        builder.add_input_address(sender)
        builder.add_output(self._output(to, value, asset))
        if reference is not None:
            metadata = Metadata({CIP20_LABEL: {"msg": _chunks(reference)}})
            builder.auxiliary_data = AuxiliaryData(AlonzoMetadata(metadata=metadata))
        try:
            signed = builder.build_and_sign([signing_key], change_address=sender)
            tx_id = str(signed.id)
            self.context.submit_tx(signed)
        except ApiError as exc:
            raise TransactionFailedError(f"rejected: {exc}") from exc
        except Exception as exc:
            raise TransactionFailedError(f"could not build the transaction: {exc}") from exc
        if not wait:
            return Receipt(self.name, self.network, tx_id, PENDING)
        return self._wait_for(tx_id)

    def _output(self, to: str, value: Decimal, asset: Asset | None) -> TransactionOutput:
        address = Address.from_primitive(to)
        if asset is None or asset.is_native:
            return TransactionOutput(address, Value(_lovelace(value)))
        if value != value.to_integral_value():
            raise ValidationError("native token amounts are whole base units")
        assert asset.issuer is not None
        tokens = MultiAsset.from_primitive(
            {bytes.fromhex(asset.issuer): {bytes.fromhex(asset.code): int(value)}}
        )
        output = TransactionOutput(address, Value(0, tokens))
        output.amount.coin = min_lovelace(self.context, output)
        return output

    def _wait_for(self, tx_id: str) -> Receipt:
        deadline = time.monotonic() + CONFIRMATION_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            try:
                return self.transaction(tx_id)
            except NotFoundError:
                time.sleep(CONFIRMATION_POLL_SECONDS)
        return Receipt(self.name, self.network, tx_id, PENDING)
