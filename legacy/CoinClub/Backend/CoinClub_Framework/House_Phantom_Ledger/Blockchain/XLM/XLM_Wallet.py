#https://stellar-sdk.readthedocs.io/_/downloads/en/latest/pdf/
from stellar_sdk import Keypair
from stellar_sdk import TransactionBuilder, Server, Network, Keypair
from stellar_sdk import Server
from stellar_sdk import Asset

class XLM_Wallet:
    def KEYPAIR(seed):
        keypair = Keypair.from_secret(seed)
        return keypair

        #test again later
    def KEYPAIR_PUB(keypair):
        public_key = keypair.public_key
        can_sign = keypair.can_sign() # True

        return can_sign
        return public_key

    def KEYPAIR_FROM_PUB(public_key):
        keypair = Keypair.from_public_key(public_key)
        can_sign = keypair.can_sign() # False

        return keypair
        return can_sign

    def KEYPAIR_GENERATE(url): #'https://friendbot.stellar.org'
        keypair = Keypair.random()

        print("Public Key: " + keypair.public_key)
        print("Secret Seed: " + keypair.secret)

        public_key = keypair.public_key
        keypair_secret = keypair.secret

        #response = requests.get(url, params={'addr': keypair.public_key})
        #return response

    def CREATE_ACCOUNT(url,pub_key):
        response = requests.get(url, params={'addr': pub_key})
        return response



#
