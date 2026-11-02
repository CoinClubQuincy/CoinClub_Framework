"""CoinClub: one Python interface across multiple blockchains."""

from .chains.base import Chain, NetworkConfig
from .errors import (
    CoinClubError,
    MainnetNotAllowedError,
    MissingDependencyError,
    NetworkError,
    NotFoundError,
    TransactionFailedError,
    UnsupportedOperationError,
    ValidationError,
)
from .models import Asset, Balance, BookOffer, Payment, Receipt, Wallet
from .registry import available_chains, connect

__version__ = "1.0.0"

__all__ = [
    "Asset",
    "Balance",
    "BookOffer",
    "Chain",
    "CoinClubError",
    "MainnetNotAllowedError",
    "MissingDependencyError",
    "NetworkConfig",
    "NetworkError",
    "NotFoundError",
    "Payment",
    "Receipt",
    "TransactionFailedError",
    "UnsupportedOperationError",
    "ValidationError",
    "Wallet",
    "available_chains",
    "connect",
]
