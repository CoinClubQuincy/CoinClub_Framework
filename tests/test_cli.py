import json
import os
import stat
from decimal import Decimal

import pytest

from coinclub.cli import main


def test_chains_lists_networks(capsys):
    assert main(["chains"]) == 0
    assert "testnet" in json.loads(capsys.readouterr().out)["xrpl"]["networks"]


def test_wallet_refuses_to_run_without_a_destination(capsys):
    assert main(["wallet", "xrpl"]) == 1
    assert "--out" in capsys.readouterr().err


def test_wallet_file_is_private_and_secret_is_not_printed(tmp_path, capsys):
    path = tmp_path / "w.wallet.json"
    assert main(["wallet", "stellar", "--out", str(path)]) == 0
    saved = json.loads(path.read_text())
    assert saved["secret"] not in capsys.readouterr().out
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o600


def test_wallet_never_overwrites_an_existing_file(tmp_path, capsys):
    path = tmp_path / "w.wallet.json"
    path.write_text("existing key")
    assert main(["wallet", "stellar", "--out", str(path)]) == 1
    assert path.read_text() == "existing key"


def test_ladder_plans_without_network(capsys):
    assert main(["ladder", "--price", "1", "--step", "0.5", "--rungs", "1", "--quantity", "2",
                 "--strategy", "bottom"]) == 0
    assert [Decimal(r["price"]) for r in json.loads(capsys.readouterr().out)] == [
        Decimal("1"),
        Decimal("1.5"),
    ]


def test_range_ladder_needs_its_bounds(capsys):
    assert main(["ladder", "--strategy", "range", "--rungs", "1", "--quantity", "2"]) == 1


def test_unknown_chain_is_a_clean_error(capsys):
    assert main(["balance", "dogecoin", "x"]) == 1
    assert "unknown chain" in capsys.readouterr().err


def test_no_command_shows_usage():
    with pytest.raises(SystemExit):
        main([])
