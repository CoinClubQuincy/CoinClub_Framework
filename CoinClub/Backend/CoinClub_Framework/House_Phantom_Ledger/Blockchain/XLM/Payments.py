#https://stellar-sdk.readthedocs.io/_/downloads/en/latest/pdf/
from stellar_sdk import Keypair
from stellar_sdk import TransactionBuilder, Server, Network, Keypair
from stellar_sdk import Server
from stellar_sdk import Asset
from stellar_sdk import Network


class Payment:
    def PAY(source_secret_key,receiver_public_key,horizon_url,Memo,amount,asset,set_timeout): # "https://horizon-testnet.stellar.org"
        """
        Create, sign, and submit a transaction using Python Stellar SDK.

        Assumes that you have the following items:
        1. Secret key of a funded account to be the source account
        2. Public key of an existing account as a recipient
            These two keys can be created and funded by the friendbot at
            https://www.stellar.org/laboratory/ under the heading "Quick Start: Test Account"
        3. Access to Python Stellar SDK (https://github.com/StellarCN/py-stellar-base) through Python shell.
        """

        # The source account is the account we will be signing and sending from.
        #source_secret_key = "SBFZCHU5645DOKRWYBXVOXY2ELGJKFRX6VGGPRYUWHQ7PMXXJNDZFMKD"

        # Derive Keypair object and public key (that starts with a G) from the secret
        source_keypair = Keypair.from_secret(source_secret_key)
        source_public_key = source_keypair.public_key

        #receiver_public_key = "GA7YNBW5CBTJZ3ZZOWX3ZNBKD6OE7A7IHUQVWMY62W2ZBG2SGZVOOPVH"

        # Configure StellarSdk to talk to the horizon instance hosted by Stellar.org
        # To use the live network, set the hostname to 'horizon.stellar.org'
        server = Server(horizon_url=horizon_url)

        # Transactions require a valid sequence number that is specific to this account.
        # We can fetch the current sequence number for the source account from Horizon.
        source_account = server.load_account(source_public_key)

        base_fee = server.fetch_base_fee()
        # we are going to submit the transaction to the test network,
        # so network_passphrase is `Network.TESTNET_NETWORK_PASSPHRASE`,
        # if you want to submit to the public network, please use `Network.PUBLIC_NETWORK_PASSPHRASE`.
        transaction = (
            TransactionBuilder(
                source_account=source_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=base_fee,
            )
                .add_text_memo(Memo)  # Add a memo
                # Add a payment operation to the transaction
                # Send 350.1234567 XLM to receiver
                # Specify 350.1234567 lumens. Lumens are divisible to seven digits past the decimal.
                .append_payment_op(receiver_public_key, str(amount), asset)
                .set_timeout(int(set_timeout))  # Make this transaction valid for the next 30 seconds only
                .build()
        )

        # Sign this transaction with the secret key
        # NOTE: signing is transaction is network specific. Test network transactions
        # won't work in the public network. To switch networks, use the Network object
        # as explained above (look for stellar_sdk.network.Network).
        transaction.sign(source_keypair)

        # Let's see the XDR (encoded in base64) of the transaction we just built
        print(transaction.to_xdr())

        # Submit the transaction to the Horizon server.
        # The Horizon server will then submit the transaction into the network for us.
        response = server.submit_transaction(transaction)
        print(response)

class Path_Payments:
    def PAY_PATH():
        server = Server(horizon_url="https://horizon-testnet.stellar.org")
        source_keypair = Keypair.from_secret("SA6XHAH4GNLRWWWF6TEVEWNS44CBNFAJWHWOPZCVZOUXSQA7BOYN7XHC")

        source_account = server.load_account(account_id=source_keypair.public_key)

        path = [
            Asset("USD", "GBBM6BKZPEHWYO3E3YKREDPQXMS4VK35YLNU7NFBRI26RAN7GI5POFBB"),
            Asset("EUR", "GDTNXRLOJD2YEBPKK7KCMR7J33AAG5VZXHAJTHIG736D6LVEFLLLKPDL")
        ]
        transaction = TransactionBuilder(
            source_account=source_account, network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE, base_fee=100) \
            .append_path_payment_strict_receive_op(destination="GBBM6BKZPEHWYO3E3YKREDPQXMS4VK35YLNU7NFBRI26RAN7GI5POFBB",
                                    send_code="XLM", send_issuer=None, send_max="1000", dest_code="GBP",
                                    dest_issuer="GASOCNHNNLYFNMDJYQ3XFMI7BYHIOCFW3GJEOWRPEGK2TDPGTG2E5EDW",
                                    dest_amount="5.50", path=path) \
            .set_timeout(30) \
            .build()
        transaction.sign(source_keypair)
        response = server.submit_transaction(transaction)
