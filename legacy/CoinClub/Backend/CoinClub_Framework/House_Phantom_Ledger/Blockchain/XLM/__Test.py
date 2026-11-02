from stellar_sdk import Keypair
from stellar_sdk import TransactionBuilder, Server, Network, Keypair
from stellar_sdk import Server
from stellar_sdk import Asset
from XLM_Wallet import XLM_Wallet

class Test:
    def __init__(self):
        print("start test")
        x = XLM_Wallet.KEYPAIR("test")
        print(x)


if "__main__" == __name__:
    Test()
