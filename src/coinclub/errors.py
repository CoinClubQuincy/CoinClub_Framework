"""Exceptions raised by coinclub. Everything derives from CoinClubError."""

from __future__ import annotations


class CoinClubError(Exception):
    """Base class for all coinclub errors."""


class ValidationError(CoinClubError, ValueError):
    """An argument was rejected before anything reached the network."""


class MainnetNotAllowedError(CoinClubError):
    """A write was attempted on a mainnet without allow_mainnet=True."""


class UnsupportedOperationError(CoinClubError):
    """The chain adapter does not support this operation."""


class NotFoundError(CoinClubError):
    """The requested account or transaction does not exist."""


class NetworkError(CoinClubError):
    """A node or API returned an error, or could not be reached."""


class TransactionFailedError(CoinClubError):
    """The network rejected a transaction, or it failed when applied."""

    def __init__(self, message: str, *, code: str | None = None, tx_id: str | None = None):
        super().__init__(message)
        self.code = code
        self.tx_id = tx_id


class MissingDependencyError(CoinClubError, ImportError):
    """An optional SDK is not installed."""

    def __init__(self, extra: str):
        super().__init__(f"this feature needs: pip install 'coinclub[{extra}]'")
        self.extra = extra
