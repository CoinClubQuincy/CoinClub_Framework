#https://stellar-sdk.readthedocs.io/_/downloads/en/latest/pdf/
from stellar_sdk import Keypair
from stellar_sdk import TransactionBuilder, Server, Network, Keypair
from stellar_sdk import Server
from stellar_sdk import Asset
from Account

class Transactions:
    def ASSETS(type,Asset_Name="",Asset_Code="",seed=""):
        if type == "native":
            native = Asset.native()
            return native

        else:
            asset = Asset(Asset_Name, Asset_Code)
            is_native = asset.is_native() # False
            asset_type =  asset_type.type

            return asset
            return asset_type

    def TRANSACTION(source,destination,Server):
        if Server == "Live":
            server = Server(horizon_url="")
        elif Server == "Test":
            server = Server(horizon_url="https://horizon-testnet.stellar.org")
        else:
            print("%s is an incorrect input" % Server)
        source = Keypair.from_secret(seed)
        destination = Keypair.random()

        source_account = server.load_account(account_id=source.public_key)
        transaction = TransactionBuilder(source_account=source_account,network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,base_fee=100) \
        .append_create_account_op(destination=destination.public_key, starting_balance="12.25") \
        .build()
        transaction.sign(source)
        response = server.submit_transaction(transaction)

        print("Transaction hash: {}".format(response["hash"]))
        print("New Keypair: \n\taccount id: {account_id}\n\tsecret seed: {secret_seed}".format(

        account_id=destination.public_key, secret_seed=destination.secret))

    def MEMO(keypair_Root,memo,destination_address,Amount,Asset_code,timeout,fee):
        root_keypair = Keypair.from_secret(keypair_Root)
        # Create an Account object from an address and sequence number.
        root_account = Account(account_id=root_keypair.public_key, sequence=1)

        transaction = TransactionBuilder(source_account=root_account, network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                                         base_fee=fee).add_text_memo(memo).append_payment_op(
            destination=destination_address, amount=Amount,
            asset_code=Asset_code).set_timeout(timeout).build()
