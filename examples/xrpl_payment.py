"""Fund two wallets on the XRP Ledger testnet, then settle an invoice with a real payment."""

from coinclub import connect
from coinclub.gateway import PaymentGateway

ledger = connect("xrpl")
customer = ledger.create_wallet()
merchant = ledger.create_wallet()
ledger.request_test_funds(customer)
ledger.request_test_funds(merchant)

gateway = PaymentGateway(ledger, merchant.address)
invoice = gateway.create_invoice("2.50")
print(f"Invoice {invoice.id}: pay {invoice.amount} XRP, reference {invoice.reference}")
print("Before payment:", gateway.check(invoice.id).status)

receipt = ledger.transfer(customer, merchant.address, invoice.amount, reference=invoice.reference)
print("Payment:", receipt.status, receipt.tx_id)
print("After payment:", gateway.check(invoice.id).status)
