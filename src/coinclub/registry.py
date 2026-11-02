"""Find and connect to chains by name."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from .chains.base import Chain
from .errors import MissingDependencyError, ValidationError

# name -> (module, class or EVM chain key, pip extra)
_CHAINS: dict[str, tuple[str, str, str]] = {
    "xrpl": ("coinclub.chains.xrpl", "XrplChain", "xrpl"),
    "stellar": ("coinclub.chains.stellar", "StellarChain", "stellar"),
    "xdc": ("coinclub.chains.evm", "XdcChain", "evm"),
    "flare": ("coinclub.chains.evm", "FlareChain", "evm"),
    "filecoin": ("coinclub.chains.evm", "FilecoinChain", "evm"),
    "ethereum": ("coinclub.chains.evm", "EthereumChain", "evm"),
    "algorand": ("coinclub.chains.algorand", "AlgorandChain", "algorand"),
    "cardano": ("coinclub.chains.cardano", "CardanoChain", "cardano"),
    "eos": ("coinclub.chains.eos", "EosChain", "all"),
}
_ALIASES = {"xrp": "xrpl", "xlm": "stellar", "fil": "filecoin", "flr": "flare", "algo": "algorand",
            "ada": "cardano", "eth": "ethereum"}


def available_chains() -> list[str]:
    return sorted(_CHAINS)


def chain_class(name: str) -> type[Chain]:
    key = _ALIASES.get(name.lower(), name.lower())
    if key not in _CHAINS:
        raise ValidationError(f"unknown chain {name!r}: use {', '.join(available_chains())}")
    module, cls, extra = _CHAINS[key]
    try:
        return getattr(import_module(module), cls)
    except ImportError as exc:
        raise MissingDependencyError(extra) from exc


def connect(
    chain: str,
    network: str | None = None,
    *,
    url: str | None = None,
    allow_mainnet: bool = False,
    **options: Any,
) -> Chain:
    """Connect to a chain. Without a network this picks the chain's test network.

    >>> ledger = connect("xrpl")                                    # testnet
    >>> ledger = connect("xrpl", "mainnet", allow_mainnet=True)     # can spend real funds
    """
    return chain_class(chain)(network, url=url, allow_mainnet=allow_mainnet, **options)
