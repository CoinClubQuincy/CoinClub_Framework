#https://stellar-sdk.readthedocs.io/_/downloads/en/latest/pdf/
from stellar_sdk import Keypair
from stellar_sdk import TransactionBuilder, Server, Network, Keypair
from stellar_sdk import Server
from stellar_sdk import Asset


class XLM_Account_Managment:
    def QUERY_HORIZON(account,url): #Querying Horizon "https://horizon-testnet.stellar.org"
        server = Server(horizon_url=url)

        # get a list of transactions that occurred in ledger 1400
        transactions = server.transactions().for_ledger(1400).call()
        print(transactions)

        # get a list of transactions submitted by a particular account
        transactions = server.transactions() \
        .for_account(account_id=account) \
        .call()
        print(transactions)

    def BUILDING_REQUEST(url,account_id): # "https://horizon-testnet.stellar.org"
        server = Server(horizon_url=url)
        transactions = server.transactions().for_ledger(1400).call()
        print(transactions)


        transactions = server.transactions() \
            .for_account(account_id=account_id) \
            .call()

        print(transactions)

    def STREAMING_REQUEST(url,account_id,last_cursor):
        server = Server(horizon_url=url)
        account_id = account_id
        last_cursor = last_cursor #'now' or load where you left off

        def tx_handler(tx_response):
            print(tx_response)

        for tx in server.transactions().for_account(account_id).cursor(last_cursor).stream():
            tx_handler(tx)


    def ASSETS():
        print("test")


#
