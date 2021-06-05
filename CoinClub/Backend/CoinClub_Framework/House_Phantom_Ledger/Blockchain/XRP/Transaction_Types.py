#https://xrpl.org/data-api.html
import requests
import json
import csv
import os
import sys
import subprocess
import re

# Folder Directories
#from File_Manager import Files

# rg5W75cDeaooC99xoJJeV9eV6U63u4GTX
class Transaction_Types:

#Transaction Types
    def ACCOUNT_SET(Account,Fee,Sequence,Domain,SetFlag,MessageKey):
        Data = """
        {
            "TransactionType": "AccountSet",
            "Account" : %s,
            "Fee": %s,
            "Sequence": %s,
            "Domain": %s,
            "SetFlag": %s,
            "MessageKey": %s
        }
        """ % (Account,Fee,int(Sequence),Domain,int(SetFlag),MessageKey)
        return Data

    def ACCOUNT_DELETE(Account,Destination,DestinationTag,Fee,Sequence,Flags):
        Data = """
        {
            "TransactionType": AccountDelete,
            "Account": %s,
            "Destination": %s,
            "DestinationTag": %s,
            "Fee": %s,
            "Sequence": %s,
            "Flags": %s
        }
        """ % (Account,Destination,int(DestinationTag),Fee,int(Sequence),int(Flags))
        return Data

    def CHECK_CANCEL(Account,CheckID,Fee):
        Data = """
        {
            "Account": %s,
            "TransactionType": CheckCancel,
            "CheckID": %s,
            "Fee": %s
        }
        """ % (Account,CheckID,Fee)
        return Data

    def CHECK_CASH(Account,Amount,CheckID,Fee):
        Data = """
        {
            "Account": %s,
            "TransactionType": CheckCash,
            "Amount": %s,
            "CheckID": %s,
            "Fee": %s
        }
        """ % (Account,Amount,CheckID,Fee)
        return Data

    def CHECK_CREATE(Account,Destination,SendMax,Expiration,InvoiceID,DestinationTag,Fee):
        Data = """
        {
          "TransactionType": "CheckCreate",
          "Account": %s,
          "Destination": %s,
          "SendMax": %s,
          "Expiration": %s,
          "InvoiceID": %s,
          "DestinationTag": %s,
          "Fee": %s
        }
        """ % (Account,Destination,SendMax,int(Expiration),InvoiceID,int(DestinationTag),Fee)
        return Data

    def DEPOSIT_PREAUTH(Account,Authorize,Fee,Flags,Sequence):
        Data = """
        {
          "TransactionType" : DepositPreauth,
          "Account" : %s,
          "Authorize" : %s,
          "Fee" : %s,
          "Flags" : %s,
          "Sequence" : %s
        }
        """ % (Account,Authorize,Fee,int(Flags),int(Sequence))
        return Data

    def ESCROW_CANCEL(Account,Owner,OfferSequence):
        Data = """
        {
            "Account": %s,
            "TransactionType": "EscrowCancel",
            "Owner": %s,
            "OfferSequence": %s,
        }
        """ % (Account,Owner,int(OfferSequence))
        return Data

    def ESCROW_CREATE(Account,Amount,Destination,CancelAfter,FinishAfter,Condition,DestinationTag,SourceTag):
        Data = """
        {
            "Account": %s,
            "TransactionType": "EscrowCreate",
            "Amount": %s,
            "Destination": %s,
            "CancelAfter": %s,
            "FinishAfter": %s,
            "Condition": "%s",
            "DestinationTag": %s,
            "SourceTag": %s
        }
        """ % (Account,Amount,Destination,int(CancelAfter),int(FinishAfter),Condition,int(DestinationTag),int(SourceTag))
        return Data

    def ESCROW_FINNISH(Account,Owner,OfferSequence,Condition,Fulfillment):
        Data = """
        {
            "Account": %s,
            "TransactionType": "EscrowFinish",
            "Owner": %s,
            "OfferSequence": %s,
            "Condition": %s,
            "Fulfillment": %s
        }
        """ % (Account,Owner,int(OfferSequence),Condition,Fulfillment)
        return Data

    def OFFER_CANCEL(Account,Fee,Flags,LastLedgerSequence,OfferSequence,Sequence):
        Data = """
        {
            "TransactionType": "OfferCancel",
            "Account": %s,
            "Fee": %s,
            "Flags": %s,
            "LastLedgerSequence": %s,
            "OfferSequence": %s,
            "Sequence": %s
        }
        """ % (Account,Fee,int(Flags),int(LastLedgerSequence),int(OfferSequence),int(Sequence))
        return Data


    def OFFER_CREATE(Account,Fee,Flags,LastLedgerSequence,Sequence,TakerGets,currency,issuer,value):
        Data = """
        {
            "TransactionType": "OfferCreate",
            "Account": %s,
            "Fee": %s,
            "Flags": %s,
            "LastLedgerSequence": %s,
            "Sequence": %s,
            "TakerGets": %s,
            "TakerPays": {
              "currency": %s,
              "issuer": %s,
              "value": %s
            }
        }
        """ % (Account,Fee,int(Flags),int(LastLedgerSequence),int(Sequence),TakerGets,currency,issuer,value)
        return Data

    def PAYMENT(Account,Destination,currency,value,issuer,Fee,Flags,Sequence):
        Data = """
        {
          "TransactionType" : "Payment",
          "Account" : %s,
          "Destination" : %s,
          "Amount" : {
             "currency" : %s,
             "value" : %s,
             "issuer" : %s
          },
          "Fee": %s,
          "Flags": %s,
          "Sequence": %s,
        }
        """ % (Account,Destination,currency,value,issuer,Fee,int(Flags),int(Sequence))
        return Data

    def PAYMENT_CHANNEL_CLAIM(Channel,Balance,Amount,Signature,PublicKey):
        Data = """
        {
          "Channel": %s,
          "Balance": %s,
          "Amount": %s,
          "Signature": %s,
          "PublicKey": %s
        }
        """ % (Channel,Balance,Amount,Signature,PublicKey)
        return Data


    def PAYMENT_CHANNEL_CREATE(Account,Amount,Destination,SettleDelay,PublicKey,CancelAfter,DestinationTag,SourceTag):
        Data = """
        {
            "Account": %s,
            "TransactionType": "PaymentChannelCreate",
            "Amount": %s,
            "Destination": %s,
            "SettleDelay": %s,
            "PublicKey": %s,
            "CancelAfter": %s,
            "DestinationTag": %s,
            "SourceTag": %s
        }
        """ % (Account,Amount,Destination,int(SettleDelay),PublicKey,int(CancelAfter),int(DestinationTag),int(SourceTag))
        return Data

    def PAYMENT_CHANNEL_FUND(Account,Channel,Amount,Expiration):
        Data = """
        {
            "Account": %s,
            "TransactionType": "PaymentChannelFund",
            "Channel": %s,
            "Amount": %s,
            "Expiration": %s
        }
        """ % (Account,Channel,Amount,int(Expiration))
        return Data

    def SET_REGULAR_KEY(Flags,Account,Fee,RegularKey):
        Data = """
        {
            "Flags": %s,
            "TransactionType": "SetRegularKey",
            "Account": %s,
            "Fee": %s,
            "RegularKey": %s
        }
        """ % (int(Flags),Account,Fee,RegularKey)
        return Data

############# MUTIVARIABLED SIGNING ############# ############# MUTIVARIABLED SIGNING ############# ############# MUTIVARIABLED SIGNING #############
    def SIGNER_LIST_SET(TransactionType_output):
        Data = """

        """

    def DEFAULT_SUBMIT_MULTISIGNED(Account,Fee,Flags,LimitAmount_currency,LimitAmount_issuer,LimitAmount_value,Sequence,Signer_Account1,Signer_SigningPubKey1,SignerTxnSignature1,Signer_Account2,Signer_SigningPubKey2,SignerTxnSignature2,SigningPubKey,TransactionType,hash):

        Data = """
            {
                "Account": %s,
                "Fee": %s,
                "Flags": %s,
                "LimitAmount": {
                    "currency": %s,
                    "issuer": %s,
                    "value": %s
                },
                "Sequence": 4,
                "Signers": [
                    {
                        "Signer": {
                            "Account": %s,
                            "SigningPubKey": %s,
                            "TxnSignature": %s
                        }
                    },
                    {
                        "Signer": {
                            "Account": %s,
                            "SigningPubKey": %s,
                            "TxnSignature": %s
                        }
                    }
                ],
                "SigningPubKey": %s,
                "TransactionType": "%s",
                "hash": "%s"
            }
            """ % (Account,Fee,int(Flags),LimitAmount_currency,LimitAmount_issuer,LimitAmount_value,int(Sequence),Signer_Account1,Signer_SigningPubKey1,SignerTxnSignature1,Signer_Account2,Signer_SigningPubKey2,SignerTxnSignature2,SigningPubKey,TransactionType,hash)

        return Data

############# MUTIVARIABLED SIGNING ############# ############# MUTIVARIABLED SIGNING ############# ############# MUTIVARIABLED SIGNING #############

    def TICKET_CREATE(Account,Fee,Sequence,TicketCount):
        Data = """
        {
            "TransactionType": "TicketCreate",
            "Account": %s,
            "Fee": %s,
            "Sequence": %s,
            "TicketCount": %s
        }
        """ % (Account,Fee,int(Sequence),int(TicketCount))
        return Data

    def TRUST_SET(Account,Fee,Flags,LastLedgerSequence,currency,issuer,value,Sequence):
        Data = """
        {
            "TransactionType": "TrustSet",
            "Account": %s,
            "Fee": %s,
            "Flags": %s,
            "LastLedgerSequence": %s,
            "LimitAmount": {
              "currency": %s,
              "issuer": %s,
              "value": %s
            },
            "Sequence": %s
        }
        """ % (Account,Fee,int(Flags),int(LastLedgerSequence),currency,issuer,value,int(Sequence))
        return Data

#Pseudo-Transactions
    def ENABLE_AMENDMENT(Account,Amendment,Fee,LedgerSequence,Sequence,SigningPubKey):
        Data = """
        {
          "Account": %s,
          "Amendment": %s,
          "Fee": %s,
          "LedgerSequence": %s,
          "Sequence": %s,
          "SigningPubKey": %s,
          "TransactionType": "EnableAmendment"
        }
        """ % (Account,Amendment,Fee,int(LedgerSequence),int(Sequence),SigningPubKey)
        return Data

    def SET_FEE(Account,BaseFee,Fee,ReferenceFeeUnits,ReserveBase,ReserveIncrement,Sequence,SigningPubKey,date,hash,ledger_index):
        Data = """
        {
            "Account": %s,
            "BaseFee": %s,
            "Fee": %s,
            "ReferenceFeeUnits": %s,
            "ReserveBase": %s,
            "ReserveIncrement": %s,
            "Sequence": %s,
            "SigningPubKey": %s,
            "TransactionType": "SetFee",
            "date": %s,
            "hash": %s,
            "ledger_index": %s,
        }
        """ % (Account,BaseFee,Fee,int(ReferenceFeeUnits),int(ReserveBase),int(ReserveIncrement),int(Sequence),SigningPubKey,int(date),hash,int(ledger_index))
        return Data

    def UNL_MODIFY(Account,Fee,LedgerSequence,Sequence,SigningPubKey,UNLModifyDisabling,UNLModifyValidator):
        Data = """
        {
          "Account": %s,
          "Fee": %s,
          "LedgerSequence": %s,
          "Sequence": %s,
          "SigningPubKey": %s,
          "TransactionType": "UNLModify",
          "UNLModifyDisabling": %s,
          "UNLModifyValidator": %s,
        }
        """ % (Account,Fee,int(LedgerSequence),int(Sequence),SigningPubKey,int(UNLModifyDisabling),UNLModifyValidator)

        return Data

class Transaction_Types_Format_Output:

    def SIGN(Comand_Output):

        Item = json.loads(Comand_Output)
        status = Item["result"]["status"]
        tx_blob = Item["result"]["tx_blob"]
        Account = Item["result"]["tx_json"]["Account"]
        currency = Item["result"]["tx_json"]["Amount"]["currency"]
        issuer = Item["result"]["tx_json"]["Amount"]["issuer"]
        value = Item["result"]["tx_json"]["Amount"]["value"]
        Destination = Item["result"]["tx_json"]["Destination"]
        Fee = Item["result"]["tx_json"]["Fee"]
        Flags = Item["result"]["tx_json"]["Flags"]
        Sequence = Item["result"]["tx_json"]["Sequence"]
        SigningPubKey = Item["result"]["tx_json"]["SigningPubKey"]
        TransactionType = Item["result"]["tx_json"]["TransactionType"]
        TxnSignature = Item["result"]["tx_json"]["TxnSignature"]
        hash = Item["result"]["tx_json"]["hash"]

        return [status,tx_blob,Account,currency,issuer,value,Destination,Fee,Flags,Sequence,SigningPubKey,TransactionType,TxnSignature,hash]

    def SIGN_FOR(Comand_Output):

        Item = json.loads(Comand_Output)
        stats = Item["result"]["status"]
        tx_blob = Item["result"]["tx_blob"]
        Account = Item["result"]["tx_json"]["Account"]
        Fee = Item["result"]["tx_json"]["Fee"]
        Flags = Item["result"]["tx_json"]["Flags"]
        currency = Item["result"]["tx_json"]["LimitAmount"]["currency"]
        issuer = Item["result"]["tx_json"]["LimitAmount"]["issuer"]
        value = Item["result"]["tx_json"]["LimitAmount"]["value"]
        Sequence = Item["result"]["tx_json"]["Sequence"]
        signer_Account = Item["result"]["tx_json"]["Signers"][0]["Signer"]["Account"]
        SigningPubKey = Item["result"]["tx_json"]["Signers"][0]["Signer"]["SigningPubKey"]
        TransactionType = Item["result"]["tx_json"]["TransactionType"]
        hash = Item["result"]["tx_json"]["hash"]

        return [stats,tx_blob,Account,Fee,Flags,currency,issuer,value,Sequence,signer_Account,SigningPubKey,TransactionType,hash]


    def SUBMIT(Comand_Output):

        Item = json.loads(Comand_Output)
        accepted = Item["result"]["accepted"]
        account_sequence_available = Item["result"]["account_sequence_available"]
        account_sequence_next = Item["result"]["account_sequence_next"]
        applied = Item["result"]["applied"]
        broadcast = Item["result"]["broadcast"]
        engine_result = Item["result"]["engine_result"]
        engine_result_code = Item["result"]["engine_result_code"]
        engine_result_message = Item["result"]["engine_result_message"]
        status = Item["result"]["status"]
        kept = Item["result"]["kept"]
        open_ledger_cost = Item["result"]["open_ledger_cost"]
        queued = Item["result"]["queued"]
        tx_blob = Item["result"]["tx_blob"]
        Account = Item["result"]["tx_json"]["Account"]
        currency = Item["result"]["tx_json"]["Amount"]["currency"]
        issuer = Item["result"]["tx_json"]["Amount"]["issuer"]
        value = Item["result"]["tx_json"]["Amount"]["value"]
        Destination = Item["result"]["tx_json"]["Destination"]
        Fee = Item["result"]["tx_json"]["Fee"]
        Flags = Item["result"]["tx_json"]["Flags"]
        Sequence = Item["result"]["tx_json"]["Sequence"]
        SigningPubKey = Item["result"]["tx_json"]["SigningPubKey"]
        TransactionType = Item["result"]["tx_json"]["TransactionType"]
        TxnSignature = Item["result"]["tx_json"]["TxnSignature"]
        hash = Item["result"]["tx_json"]["hash"]
        validated_ledger_index = Item["validated_ledger_index"]

        return [accepted,account_sequence_available,account_sequence_next,applied,broadcast,engine_result,engine_result_code,
        engine_result_message,status,kept,open_ledger_cost,queued,tx_blob,Account,currency,issuer,value,Destination,Fee,Flags,
        Sequence,SigningPubKey,TransactionType,TxnSignature,hash,validated_ledger_index]


    def DEFAULT_SUBMIT_MULTISIGNED():
        print("")


class Path_finder:
    def PATH_FINDER_INPUT(source_account,currencyA,currencyB,destination_account,value,issuer):
        Data = """
        {
           "source_account": %s,
           "source_currencies":[
              {
                 "currency": %s
              },
              {
                 "currency": %s
              }
           ],
           "destination_account": %s,
           "destination_amount":{
              "value": %s,
              "currency": %s,
              "issuer": %s
           }
        }
        """ % (source_account,currencyA,currencyB,destination_account,value,currencyB,issuer)

        return Data


class Error_Formatting:
    def ErrorHandeling(Data):
        Item = json.loads(output)

        error = Item["result"]["error"]
        account = Item["result"]["request"]["account"]
        command = Item["result"]["request"]["command"]
        ledger_index = Item["result"]["request"]["ledger_index"]
        strict = Item["result"]["request"]["strict"]
        status = Item["result"]["status"]

        print("""Account: %s
                 Command: %s
                 Error: %s
                 Ledger_index: %s
                 Strict: %s
                 Status: %s
                """ % (account,command,error,ledger_index,strict,status))


#
