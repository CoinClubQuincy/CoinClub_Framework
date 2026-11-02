"""Command line interface. Run `coinclub --help`."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from .errors import CoinClubError, MissingDependencyError
from .exchange import BitrueClient
from .liquidity import bottom, from_range, mean, stable, top
from .models import Asset
from .registry import available_chains, chain_class, connect

LADDERS = {"mean": mean, "top": top, "bottom": bottom, "stable": stable}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="coinclub", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("chains", help="list chains and their networks")

    wallet = commands.add_parser("wallet", help="generate a wallet locally")
    wallet.add_argument("chain")
    wallet.add_argument("--network")
    wallet.add_argument("--out", help="write the wallet to this new file, readable only by you")
    wallet.add_argument("--print-secret", action="store_true", help="print the secret")

    balance = commands.add_parser("balance", help="show an address's balances")
    balance.add_argument("chain")
    balance.add_argument("address")
    balance.add_argument("--network")

    tx = commands.add_parser("tx", help="show a transaction's status")
    tx.add_argument("chain")
    tx.add_argument("tx_id")
    tx.add_argument("--network")

    book = commands.add_parser("book", help="show a DEX order book")
    book.add_argument("chain")
    book.add_argument("base", help="CODE, or CODE:ISSUER for a token")
    book.add_argument("quote", help="CODE, or CODE:ISSUER for a token")
    book.add_argument("--network")
    book.add_argument("--limit", type=int, default=20)

    ticker = commands.add_parser("ticker", help="show a Bitrue 24-hour ticker")
    ticker.add_argument("symbol", help="market, such as XRPUSDT")

    ladder = commands.add_parser("ladder", help="plan a ladder of offers. Places nothing")
    ladder.add_argument("--strategy", choices=[*LADDERS, "range"], default="mean")
    ladder.add_argument("--price", help="centre, ceiling, floor or peg price")
    ladder.add_argument("--step", help="price gap per rung. For stable, the fraction per rung")
    ladder.add_argument("--low")
    ladder.add_argument("--high")
    ladder.add_argument("--rungs", type=int, required=True)
    ladder.add_argument("--quantity", required=True)
    return parser


def _describe_chain(name: str) -> dict[str, Any]:
    try:
        cls = chain_class(name)
    except MissingDependencyError as exc:
        return {"installed": False, "install": f"pip install 'coinclub[{exc.extra}]'"}
    return {"installed": True, "default": cls.default_network, "networks": sorted(cls.networks)}


def _asset(text: str) -> Asset:
    code, _, issuer = text.partition(":")
    return Asset(code, issuer or None)


def _emit(value: Any) -> None:
    print(json.dumps(value, indent=2, default=str))


def _write_wallet(path: str, payload: dict[str, str]) -> None:
    # O_EXCL refuses to overwrite, so an existing key cannot be destroyed by accident.
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as handle:
        json.dump(payload, handle, indent=2)


def _run(args: argparse.Namespace) -> None:
    if args.command == "chains":
        _emit({name: _describe_chain(name) for name in available_chains()})
    elif args.command == "wallet":
        if not args.out and not args.print_secret:
            raise CoinClubError("choose where the secret goes: --out FILE or --print-secret")
        chain = connect(args.chain, args.network)
        created = chain.create_wallet()
        summary = {"chain": created.chain, "network": chain.network, "address": created.address}
        if args.out:
            _write_wallet(args.out, {**summary, "secret": created.secret})
            summary["file"] = args.out
        if args.print_secret:
            summary["secret"] = created.secret
        _emit(summary)
    elif args.command == "balance":
        chain = connect(args.chain, args.network)
        _emit([
            {"code": b.asset.code, "issuer": b.asset.issuer, "amount": b.amount}
            for b in chain.balances(args.address)
        ])
    elif args.command == "tx":
        receipt = connect(args.chain, args.network).transaction(args.tx_id)
        _emit({"chain": receipt.chain, "network": receipt.network, "tx_id": receipt.tx_id,
               "status": receipt.status})
    elif args.command == "book":
        offers = connect(args.chain, args.network).order_book(
            _asset(args.base), _asset(args.quote), limit=args.limit
        )
        _emit([{"price": o.price, "amount": o.amount} for o in offers])
    elif args.command == "ticker":
        _emit(vars(BitrueClient().ticker(args.symbol)))
    elif args.command == "ladder":
        if args.strategy == "range":
            if not args.low or not args.high:
                raise CoinClubError("the range strategy needs --low and --high")
            plan = from_range(args.low, args.high, args.rungs, args.quantity)
        else:
            if not args.price or not args.step:
                raise CoinClubError(f"the {args.strategy} strategy needs --price and --step")
            plan = LADDERS[args.strategy](args.price, args.step, args.rungs, args.quantity)
        _emit([{"price": rung.price, "quantity": rung.quantity} for rung in plan])


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        _run(args)
    except (CoinClubError, FileExistsError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
