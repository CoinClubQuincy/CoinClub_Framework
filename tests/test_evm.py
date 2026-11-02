"""Real signing and execution against an in-process EVM. No network is used."""

from decimal import Decimal

import pytest
from eth_tester import EthereumTester, PyEVMBackend
from web3 import EthereumTesterProvider, Web3
from web3.exceptions import ContractLogicError

from coinclub import (
    Asset,
    MainnetNotAllowedError,
    NetworkError,
    NotFoundError,
    TransactionFailedError,
    ValidationError,
    connect,
)
from coinclub.chains.evm import EthereumChain, XdcChain

# Runtime code that returns 6 for every call. As ABI, that means decimals() == 6,
# balanceOf(x) == 6 and transfer(...) succeeds, which exercises the whole ERC-20 path.
RETURNS_SIX = "0x600a600c600039600a6000f3" + "60066000526020" + "6000f3"


@pytest.fixture
def chain():
    return EthereumChain("sepolia", provider=EthereumTesterProvider(EthereumTester(PyEVMBackend())))


@pytest.fixture
def funded(chain):
    wallet = chain.create_wallet()
    faucet = chain.web3.eth.accounts[0]
    tx = {"from": faucet, "to": wallet.address, "value": Web3.to_wei(10, "ether")}
    chain.web3.eth.wait_for_transaction_receipt(chain.web3.eth.send_transaction(tx))
    return wallet


def deploy(chain, code):
    faucet = chain.web3.eth.accounts[0]
    tx_hash = chain.web3.eth.send_transaction({"from": faucet, "data": code})
    return chain.web3.eth.wait_for_transaction_receipt(tx_hash)["contractAddress"]


def test_transfer_moves_exact_value(chain, funded):
    to = chain.create_wallet().address
    receipt = chain.transfer(funded, to, "1.25")
    assert receipt.confirmed
    assert chain.balance(to) == Decimal("1.25")
    assert chain.transaction(receipt.tx_id).confirmed


def test_wait_false_returns_a_transaction_id(chain, funded):
    receipt = chain.transfer(funded, chain.create_wallet().address, "1", wait=False)
    assert receipt.tx_id.startswith("0x")


def test_reference_is_carried_as_transaction_data(chain, funded):
    receipt = chain.transfer(funded, chain.create_wallet().address, "1", reference="order-7")
    tx = chain.web3.eth.get_transaction(receipt.tx_id)
    assert bytes(tx["input"]) == b"order-7"


def test_token_balance_uses_token_decimals(chain, funded):
    token = deploy(chain, RETURNS_SIX)
    assert chain.balance(funded.address, Asset("TOK", token)) == Decimal("0.000006")


def test_token_transfer_signs_and_confirms(chain, funded):
    token = deploy(chain, RETURNS_SIX)
    to = chain.create_wallet().address
    receipt = chain.transfer(funded, to, "1.5", asset=Asset("TOK", token))
    assert receipt.confirmed


def test_token_transfer_rejects_more_precision_than_the_token_has(chain, funded):
    token = deploy(chain, RETURNS_SIX)
    with pytest.raises(ValidationError, match="decimal places"):
        chain.transfer(funded, chain.create_wallet().address, "0.0000001", asset=Asset("T", token))


def test_token_transfer_rejects_a_reference(chain, funded):
    token = deploy(chain, RETURNS_SIX)
    with pytest.raises(ValidationError):
        chain.transfer(funded, funded.address, "1", asset=Asset("T", token), reference="x")


def test_mined_transaction_with_failed_status_raises(chain, funded, monkeypatch):
    """A transaction can be mined and still fail. Its receipt must not read as success."""
    monkeypatch.setattr(chain.web3.eth, "send_raw_transaction", lambda _raw: b"\x01" * 32)
    monkeypatch.setattr(
        chain.web3.eth, "wait_for_transaction_receipt", lambda _h, timeout: {"status": 0}
    )
    with pytest.raises(TransactionFailedError, match="reverted"):
        chain.transfer(funded, chain.create_wallet().address, "1")


def test_transfer_that_would_revert_raises_at_estimation(chain, funded, monkeypatch):
    """Real nodes report a revert during gas estimation as ContractLogicError."""

    def reverts(_tx):
        raise ContractLogicError("execution reverted")

    monkeypatch.setattr(chain.web3.eth, "estimate_gas", reverts)
    with pytest.raises(TransactionFailedError, match="would revert"):
        chain.transfer(funded, chain.create_wallet().address, "1")


def test_unknown_transaction_raises(chain):
    with pytest.raises(NotFoundError):
        chain.transaction("0x" + "ab" * 32)


def test_wrong_chain_id_stops_before_sending(chain, funded):
    chain.expected_chain_id = 50
    start = chain.web3.eth.get_transaction_count(funded.address)
    with pytest.raises(NetworkError, match="expected"):
        chain.transfer(funded, chain.create_wallet().address, "1")
    assert chain.web3.eth.get_transaction_count(funded.address) == start


def test_wallet_round_trip(chain):
    wallet = chain.create_wallet()
    assert chain.wallet_from_secret(wallet.secret).address == wallet.address


def test_bad_key_is_rejected_without_quoting_it(chain):
    with pytest.raises(ValidationError) as caught:
        chain.wallet_from_secret("0xnotakey")
    assert "0xnotakey" not in str(caught.value)


def test_xdc_prefixed_addresses_are_accepted(chain):
    address = chain.create_wallet().address
    assert XdcChain.normalize_address("xdc" + address[2:]) == "0x" + address[2:]
    assert connect("xdc").is_valid_address("xdc" + address[2:])


@pytest.mark.parametrize(
    ("chain_name", "network"),
    [("xdc", "mainnet"), ("flare", "mainnet"), ("flare", "songbird"), ("filecoin", "mainnet"),
     ("ethereum", "mainnet")],
)
def test_mainnet_write_is_blocked_before_any_network_use(chain_name, network):
    chain = connect(chain_name, network)
    wallet = chain.create_wallet()
    with pytest.raises(MainnetNotAllowedError):
        chain.transfer(wallet, wallet.address, "1")


@pytest.mark.parametrize(
    ("chain_name", "ids"),
    [("xdc", {"mainnet": 50, "apothem": 51}),
     ("flare", {"mainnet": 14, "songbird": 19, "coston": 16, "coston2": 114}),
     ("filecoin", {"mainnet": 314, "calibration": 314159}),
     ("ethereum", {"mainnet": 1, "sepolia": 11155111})],
)
def test_chain_ids(chain_name, ids):
    for network, chain_id in ids.items():
        assert connect(chain_name, network).expected_chain_id == chain_id
