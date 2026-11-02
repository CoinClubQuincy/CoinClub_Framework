"""End-to-end tests against public test networks. Run with: pytest -m live

These use faucets and throwaway wallets, so no real funds are involved. Public test networks
are sometimes down or rate limited, so a failure here can be the network's fault.
"""

from __future__ import annotations

import time
from decimal import Decimal

import pytest
from xrpl.models.transactions import SignerEntry

from coinclub import Asset, MainnetNotAllowedError, TransactionFailedError, connect
from coinclub.exchange import BitrueClient
from coinclub.gateway import PAID, PaymentGateway
from coinclub.liquidity import bottom, place_ladder

pytestmark = pytest.mark.live


def funded(chain, retries=3):
    wallet = chain.create_wallet()
    for attempt in range(retries):
        try:
            chain.request_test_funds(wallet)
            return wallet
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(10)
    raise AssertionError("unreachable")


@pytest.fixture(scope="module")
def xrpl_setup():
    chain = connect("xrpl")
    return chain, funded(chain), funded(chain)


@pytest.fixture(scope="module")
def stellar_setup():
    chain = connect("stellar")
    return chain, funded(chain), funded(chain)


class TestXrplTestnet:
    def test_transfer_and_read_back(self, xrpl_setup):
        chain, alice, bob = xrpl_setup
        before = chain.balance(bob.address)
        receipt = chain.transfer(alice, bob.address, "1.5", reference="77")
        assert receipt.confirmed
        assert chain.transaction(receipt.tx_id).confirmed
        assert chain.balance(bob.address) == before + Decimal("1.5")

    def test_incoming_payment_shows_delivered_amount_and_tag(self, xrpl_setup):
        chain, alice, bob = xrpl_setup
        receipt = chain.transfer(alice, bob.address, "2", reference="4242")
        match = next(p for p in chain.incoming_payments(bob.address) if p.tx_id == receipt.tx_id)
        assert match.amount == 2
        assert match.reference == "4242"
        assert match.sender == alice.address
        assert match.timestamp is not None

    def test_gateway_settles_a_real_payment(self, xrpl_setup):
        chain, alice, bob = xrpl_setup
        gateway = PaymentGateway(chain, bob.address)
        invoice = gateway.create_invoice("1.25")
        assert gateway.check(invoice.id).status == "open"
        receipt = chain.transfer(alice, bob.address, "1.25", reference=invoice.reference)
        settled = gateway.check(invoice.id)
        assert settled.status == PAID
        assert settled.tx_id == receipt.tx_id

    def test_issue_token_then_trade_it_on_the_dex(self, xrpl_setup):
        chain, issuer, holder = xrpl_setup
        token = Asset("CCB", issuer.address)
        chain.submit(issuer, "AccountSet", set_flag=8)  # asfDefaultRipple
        assert chain.add_trustline(holder, token).confirmed
        assert chain.transfer(issuer, holder.address, "100", asset=token).confirmed
        assert chain.balance(holder.address, token) == 100

        receipt = chain.place_offer(holder, selling=token, buying=chain.native,
                                    amount="10", price="2")
        assert receipt.confirmed
        book = chain.order_book(token, chain.native)
        assert any(o.amount == 10 and o.price == 2 for o in book)

        sequence = receipt.raw["tx_json"]["Sequence"]
        assert chain.cancel_offer(holder, sequence).confirmed
        assert not any(o.amount == 10 for o in chain.order_book(token, chain.native))

    def test_ladder_places_real_offers(self, xrpl_setup):
        chain, issuer, holder = xrpl_setup
        token = Asset("CCB", issuer.address)
        plan = bottom("3", "0.5", 1, "1")
        receipts = place_ladder(chain, holder, plan, selling=token, buying=chain.native)
        assert all(r.confirmed for r in receipts)
        prices = {o.price for o in chain.order_book(token, chain.native)}
        assert {Decimal("3"), Decimal("3.5")} <= prices

    def test_any_transaction_type_by_name(self, xrpl_setup):
        chain, alice, _ = xrpl_setup
        assert chain.submit(alice, "TicketCreate", ticket_count=1).confirmed

    def test_multisigned_transaction(self, xrpl_setup):
        chain, alice, bob = xrpl_setup
        account, signer_a, signer_b = funded(chain), chain.create_wallet(), chain.create_wallet()
        chain.submit(
            account,
            "SignerListSet",
            signer_quorum=2,
            signer_entries=[
                SignerEntry(account=signer_a.address, signer_weight=1),
                SignerEntry(account=signer_b.address, signer_weight=1),
            ],
        )
        tx = chain.prepare_multisigned(account.address, "AccountSet", 2)
        signed = [chain.sign_for(signer_a, tx), chain.sign_for(signer_b, tx)]
        assert chain.submit_multisigned(tx, signed).confirmed

    def test_overspending_raises(self, xrpl_setup):
        chain, alice, bob = xrpl_setup
        with pytest.raises(TransactionFailedError):
            chain.transfer(alice, bob.address, "99999999")

    def test_rpc_read_methods(self, xrpl_setup):
        chain, alice, _ = xrpl_setup
        assert chain.account_info(account=alice.address)["account_data"]["Account"] == alice.address
        assert "info" in chain.server_info()


class TestStellarTestnet:
    def test_transfer_and_read_back(self, stellar_setup):
        chain, alice, bob = stellar_setup
        before = chain.balance(bob.address)
        receipt = chain.transfer(alice, bob.address, "1.5", reference="order-7")
        assert receipt.confirmed
        assert chain.transaction(receipt.tx_id).confirmed
        assert chain.balance(bob.address) == before + Decimal("1.5")

    def test_incoming_payment_shows_memo(self, stellar_setup):
        chain, alice, bob = stellar_setup
        receipt = chain.transfer(alice, bob.address, "2", reference="4242")
        match = next(p for p in chain.incoming_payments(bob.address) if p.tx_id == receipt.tx_id)
        assert match.amount == 2
        assert match.reference == "4242"
        assert match.sender == alice.address

    def test_gateway_settles_a_real_payment(self, stellar_setup):
        chain, alice, bob = stellar_setup
        gateway = PaymentGateway(chain, bob.address)
        invoice = gateway.create_invoice("1.25")
        assert gateway.check(invoice.id).status == "open"
        receipt = chain.transfer(alice, bob.address, "1.25", reference=invoice.reference)
        settled = gateway.check(invoice.id)
        assert settled.status == PAID
        assert settled.tx_id == receipt.tx_id

    def test_create_account(self, stellar_setup):
        chain, alice, _ = stellar_setup
        new = chain.create_wallet()
        assert chain.create_account(alice, new.address, "5").confirmed
        assert chain.balance(new.address) == 5

    def test_issue_token_then_trade_it_on_the_dex(self, stellar_setup):
        chain, issuer, holder = stellar_setup
        token = Asset("CCB", issuer.address)
        assert chain.add_trustline(holder, token).confirmed
        assert chain.transfer(issuer, holder.address, "100", asset=token).confirmed
        assert chain.balance(holder.address, token) == 100

        assert chain.place_offer(holder, selling=token, buying=chain.native,
                                 amount="10", price="2").confirmed
        book = chain.order_book(token, chain.native)
        assert any(o.amount == 10 and o.price == 2 for o in book)

        offer_id = int(chain.offers(holder.address)[0]["id"])
        assert chain.cancel_offer(holder, offer_id, selling=token, buying=chain.native).confirmed
        assert chain.offers(holder.address) == []

    def test_transfer_to_missing_account_raises(self, stellar_setup):
        chain, alice, _ = stellar_setup
        with pytest.raises(TransactionFailedError):
            chain.transfer(alice, chain.create_wallet().address, "1")


@pytest.mark.parametrize(
    ("name", "network", "expected_id"),
    [("xdc", "apothem", 51), ("flare", "coston2", 114), ("filecoin", "calibration", 314159),
     ("ethereum", "sepolia", 11155111)],
)
def test_evm_reads_a_real_node(name, network, expected_id):
    chain = connect(name, network)
    assert chain.web3.eth.chain_id == expected_id
    assert chain.balance(chain.create_wallet().address) == 0


def test_algorand_reads_a_real_node():
    chain = connect("algorand")
    assert chain.balance(chain.create_wallet().address) == 0
    assert chain.incoming_payments(chain.create_wallet().address) == []


def test_eos_reads_a_real_node():
    chain = connect("eos", "mainnet")
    assert chain.info()["head_block_num"] > 0
    assert chain.balance("eosio.token") >= 0


def test_mainnet_reads_work_but_writes_stay_blocked():
    chain = connect("xrpl", "mainnet")
    assert chain.server_info()
    wallet = chain.create_wallet()
    with pytest.raises(MainnetNotAllowedError):
        chain.transfer(wallet, wallet.address, "1")


def test_bitrue_ticker_is_real():
    assert BitrueClient().ticker("XRPUSDT").last > 0
