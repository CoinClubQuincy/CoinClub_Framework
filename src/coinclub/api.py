"""A read-only, metered HTTP API, as an AWS Lambda handler for API Gateway HTTP APIs.

It never accepts keys and never signs anything. Every call needs an API key in the x-api-key
header, and calls are counted per key per month so usage can be billed.

Routes:
    GET /v1/chains
    GET /v1/{chain}/{network}/balances/{address}
    GET /v1/{chain}/{network}/transactions/{tx_id}

Deploy it with the serverless-api blueprint from the AWS CloudFormation Infrastructure Library,
using Handler coinclub.api.handler. That blueprint passes the table name in APP_CONFIG.
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Callable
from typing import Any

from .chains.base import Chain
from .errors import (
    CoinClubError,
    MissingDependencyError,
    NetworkError,
    NotFoundError,
    UnsupportedOperationError,
    ValidationError,
)
from .registry import available_chains, connect

logger = logging.getLogger(__name__)

Authorizer = Callable[[str], bool]
Connector = Callable[[str, str], Chain]


def _response(status: int, body: Any) -> dict[str, Any]:
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json", "cache-control": "no-store"},
        "body": json.dumps(body),
    }


def _error(status: int, message: str) -> dict[str, Any]:
    return _response(status, {"error": message})


def make_handler(authorize: Authorizer, connector: Connector = connect) -> Callable[..., Any]:
    """Build a Lambda handler from an API key check and a way to connect to chains."""

    def route(event: dict[str, Any]) -> dict[str, Any]:
        method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
        if method != "GET":
            return _error(405, "this API is read-only")
        parts = [part for part in event.get("rawPath", "").split("/") if part]
        if parts == ["v1", "chains"]:
            return _response(200, {"chains": available_chains()})
        if len(parts) != 5 or parts[0] != "v1":
            return _error(404, "no such route")
        _, chain_name, network, resource, identifier = parts
        if resource not in ("balances", "transactions"):
            return _error(404, "no such route")
        chain = connector(chain_name, network)
        if resource == "balances":
            balances = chain.balances(identifier)
            return _response(
                200,
                {
                    "chain": chain.name,
                    "network": chain.network,
                    "address": identifier,
                    "balances": [
                        {
                            "code": item.asset.code,
                            "issuer": item.asset.issuer,
                            "amount": str(item.amount),
                        }
                        for item in balances
                    ],
                },
            )
        receipt = chain.transaction(identifier)
        return _response(
            200,
            {
                "chain": receipt.chain,
                "network": receipt.network,
                "tx_id": receipt.tx_id,
                "status": receipt.status,
            },
        )

    def handler(event: dict[str, Any], _context: Any = None) -> dict[str, Any]:
        headers = {name.lower(): value for name, value in (event.get("headers") or {}).items()}
        key = headers.get("x-api-key")
        if not key or not authorize(key):
            return _error(401, "a valid x-api-key header is required")
        try:
            return route(event)
        except NotFoundError:
            return _error(404, "not found")
        except (ValidationError, UnsupportedOperationError) as exc:
            return _error(400, str(exc))
        except NetworkError:
            logger.exception("upstream failure")
            return _error(502, "the upstream node failed")
        except MissingDependencyError:
            logger.exception("missing SDK")
            return _error(501, "this chain is not installed on this deployment")
        except CoinClubError:
            logger.exception("request failed")
            return _error(500, "internal error")

    return handler


def handler(event: dict[str, Any], context: Any = None) -> dict[str, Any]:
    """Lambda entry point. Reads the DynamoDB table name from APP_CONFIG."""
    global _default_handler
    if _default_handler is None:
        from .aws import DynamoApiKeys

        _default_handler = make_handler(DynamoApiKeys(os.environ["APP_CONFIG"]).authorize)
    return _default_handler(event, context)


_default_handler: Callable[..., Any] | None = None
