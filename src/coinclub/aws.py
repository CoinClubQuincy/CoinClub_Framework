"""AWS integrations: load wallets from secret stores, and keep invoices and API keys in DynamoDB.

The DynamoDB classes use one table with a string partition key named pk, which is what the
database/dynamodb-table template in the AWS CloudFormation Infrastructure Library creates.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError as exc:
    from .errors import MissingDependencyError

    raise MissingDependencyError("aws") from exc

from .chains.base import Chain
from .errors import NetworkError
from .gateway import Invoice
from .models import Asset, Wallet

KEY_PREFIX = "ccl_"


def wallet_from_secrets_manager(chain: Chain, secret_id: str, *, client: Any = None) -> Wallet:
    """Load a wallet whose secret is the plain SecretString of a Secrets Manager secret."""
    client = client or boto3.client("secretsmanager")
    try:
        secret = client.get_secret_value(SecretId=secret_id)["SecretString"]
    except ClientError as exc:
        raise NetworkError(f"could not read {secret_id}: {exc.response['Error']['Code']}") from exc
    return chain.wallet_from_secret(secret)


def wallet_from_ssm(chain: Chain, name: str, *, client: Any = None) -> Wallet:
    """Load a wallet from an SSM SecureString parameter."""
    client = client or boto3.client("ssm")
    try:
        secret = client.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]
    except ClientError as exc:
        raise NetworkError(f"could not read {name}: {exc.response['Error']['Code']}") from exc
    return chain.wallet_from_secret(secret)


def _table(table: Any) -> Any:
    return boto3.resource("dynamodb").Table(table) if isinstance(table, str) else table


class DynamoInvoiceStore:
    """Invoice store for PaymentGateway. Implements the InvoiceStore protocol."""

    def __init__(self, table: Any):
        self.table = _table(table)

    def save(self, invoice: Invoice) -> None:
        item = {
            "pk": f"INVOICE#{invoice.id}",
            "id": invoice.id,
            "chain": invoice.chain,
            "network": invoice.network,
            "address": invoice.address,
            "asset_code": invoice.asset.code,
            "amount": str(invoice.amount),
            "reference": invoice.reference,
            "created_at": str(invoice.created_at),
            "expires_at": str(invoice.expires_at),
            "status": invoice.status,
        }
        if invoice.asset.issuer is not None:
            item["asset_issuer"] = invoice.asset.issuer
        if invoice.tx_id is not None:
            item["tx_id"] = invoice.tx_id
        if invoice.paid_amount is not None:
            item["paid_amount"] = str(invoice.paid_amount)
        self.table.put_item(Item=item)
        self.table.put_item(Item={"pk": self._reference_key(invoice), "invoice": invoice.id})

    def get(self, invoice_id: str) -> Invoice | None:
        item = self.table.get_item(Key={"pk": f"INVOICE#{invoice_id}"}).get("Item")
        if item is None:
            return None
        return Invoice(
            id=item["id"],
            chain=item["chain"],
            network=item["network"],
            address=item["address"],
            asset=Asset(item["asset_code"], item.get("asset_issuer")),
            amount=Decimal(item["amount"]),
            reference=item["reference"],
            created_at=float(item["created_at"]),
            expires_at=float(item["expires_at"]),
            status=item["status"],
            tx_id=item.get("tx_id"),
            paid_amount=Decimal(item["paid_amount"]) if "paid_amount" in item else None,
        )

    def reference_in_use(self, chain: str, network: str, address: str, reference: str) -> bool:
        key = f"REFERENCE#{chain}#{network}#{address}#{reference}"
        return "Item" in self.table.get_item(Key={"pk": key})

    @staticmethod
    def _reference_key(invoice: Invoice) -> str:
        return f"REFERENCE#{invoice.chain}#{invoice.network}#{invoice.address}#{invoice.reference}"


def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def _month(now: datetime | None = None) -> str:
    return (now or datetime.now(UTC)).strftime("%Y-%m")


class DynamoApiKeys:
    """API keys and per-month call counts. Only a hash of each key is stored."""

    def __init__(self, table: Any):
        self.table = _table(table)

    def create_key(self, owner: str) -> str:
        """Create a key and return it. It cannot be recovered later."""
        key = KEY_PREFIX + secrets.token_urlsafe(32)
        self.table.put_item(
            Item={"pk": f"APIKEY#{_hash_key(key)}", "owner": owner, "active": True}
        )
        return key

    def revoke_key(self, key: str) -> None:
        self.table.update_item(
            Key={"pk": f"APIKEY#{_hash_key(key)}"},
            UpdateExpression="SET active = :off",
            ExpressionAttributeValues={":off": False},
        )

    def authorize(self, key: str) -> bool:
        """Return whether a key is active, and count the call if it is."""
        hashed = _hash_key(key)
        item = self.table.get_item(Key={"pk": f"APIKEY#{hashed}"}).get("Item")
        if not item or not item.get("active"):
            return False
        self.table.update_item(
            Key={"pk": f"USAGE#{hashed}#{_month()}"},
            UpdateExpression="ADD calls :one",
            ExpressionAttributeValues={":one": 1},
        )
        return True

    def usage(self, key: str, month: str | None = None) -> int:
        """Return the calls a key made in a month, formatted YYYY-MM. The default is this month."""
        pk = f"USAGE#{_hash_key(key)}#{month or _month()}"
        item = self.table.get_item(Key={"pk": pk}).get("Item")
        return int(item["calls"]) if item else 0


