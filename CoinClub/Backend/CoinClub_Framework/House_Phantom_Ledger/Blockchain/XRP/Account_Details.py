import requests
import json
import csv
import os
import sys
import subprocess
import re

class Account_Details:
    #account_channels
    def ACCOUNT_CHANNELS(account):
        DATA = "rippled account_channels %s " % (account)
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]

        Item = json.loads(output)
        channels = Item["result"]["channels"]
        account = Item["result"]["account"]
        channels = Item["result"]["channels"]
        ledger_index = Item["result"]["ledger_current_index"]
        status = Item["result"]["status"]
        validated = Item["result"]["validated"]

        #after test return data
        return [account,channels,ledger_index,status,validated]

    #rippled account_currencies account [ledger_index|ledger_hash] [strict]
    def ACCOUNT_CURRENCIES(account):
        DATA = "rippled account_currencies %s" % (account)
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]

        Item = json.loads(output)
        receive_currencies = Item["result"]["receive_currencies"]
        send_currencies = Item["result"]["send_currencies"]
        status = Item["result"]["status"]
        validated = Item["result"]["validated"]

        #after test return data
        return [receive_currencies,send_currencies,status,validated]

    def ACCOUNT_INFO(account):
        DATA = "rippled account_info %s" % (account)
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]

        Item = json.loads(output)
        Account = Item["result"]["account_data"]["Account"]
        Balance = Item["result"]["account_data"]["Balance"]
        Flags = Item["result"]["account_data"]["Flags"]
        LedgerEntryType = Item["result"]["account_data"]["LedgerEntryType"]
        OwnerCount = Item["result"]["account_data"]["OwnerCount"]
        PreviousTxnID = Item["result"]["account_data"]["PreviousTxnID"]
        PreviousTxnLgrSeq = Item["result"]["account_data"]["PreviousTxnLgrSeq"]
        Sequence = Item["result"]["account_data"]["Sequence"]
        index = Item["result"]["account_data"]["index"]

        ledger_index = Item["result"]["ledger_current_index"]
        status = Item["result"]["status"]
        validated = Item["result"]["validated"]

        return [Account,Balance,Flags,LedgerEntryType,OwnerCount,
                PreviousTxnID,PreviousTxnLgrSeq,Sequence,
                index,ledger_index,status,validated]

    def ACCOUNT_LINES(account):
        DATA = "rippled account_lines %s" % (account)
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]

        Item = json.loads(output)
        account = Item["result"]["account"]
        ledger_current_index = Item["result"]["ledger_current_index"]
        lines = Item["result"]["lines"]
        status = Item["result"]["status"]
        validated = Item["result"]["validated"]

        return [account,ledger_current_index,lines,status,validated]


    def ACCOUNT_OBJECTS(account):
        DATA = "rippled account_objects %s" % (account)
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]

        Item = json.loads(output)
        account = Item["result"]["account"]
        account_objects = Item["result"]["account_objects"][0]
        ledger_index = Item["result"]["ledger_current_index"]
        status = Item["result"]["status"]
        validated = Item["result"]["validated"]

        return [account,account_objects,ledger_index,status,validated]

    def ACCOUNT_OFFERS(account):
        DATA = "rippled account_offers %s" % (account)
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]

        Item = json.loads(output)
        account = Item["result"]["account"]
        ledger_current_index = Item["result"]["ledger_current_index"]
        offers = Item["result"]["offers"]
        status = Item["result"]["status"]
        validated = Item["result"]["validated"]

        return [account,ledger_current_index,offers,status,validated]


    def ACCOUNT_TX(accountID):
        DATA = "rippled -- account_tx %s" % (accountID)
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]

        Item = json.loads(output)
        account = Item["result"]["account"]
        ledger_index_max = Item["result"]["ledger_index_max"]
        ledger_index_min = Item["result"]["ledger_index_min"]
        limit = Item["result"]["limit"]
        status = Item["result"]["status"]
        transactions = Item["result"]["transactions"]
        validated = Item["result"]["validated"]

        return [account,ledger_index_max,ledger_index_min,limit,status,transactions,validated]

    def BOOK_OFFERS(taker_pays,taker_gets):
        DATA = "rippled book_offers %s %s" % (taker_pays,taker_gets)
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]


        Item = json.loads(output)
        ledger_current_index = Item["result"]["ledger_current_index"]
        offers = Item["result"]["offers"]
        status = Item["result"]["status"]
        validated = Item["result"]["validated"]

        return [ledger_current_index,offers,status,validated]

    def CAN_DELETE(ledger_index):
        proc = "rippled can_delete %s" % (ledger_index)
        output=proc.communicate()[0]
        Data = json.loads(output)

        Item = json.loads(Data)
        account_data = Item["result"]["account_data"]
        ledger_index = Item["result"]["ledger_index"]
        status = Item["result"]["status"]

        return [account_data,ledger_index,status]

        # check again
    def CHANNEL_AUTHORIZE(private_key,channel_id,drops):
        proc = "rippled channel_authorize %s %s %s" % (private_key,channel_id,drops)
        output=proc.communicate()[0]
        Data = json.loads(output)

        Item = json.loads(Data)
        status = Item["result"]["status"]
        signature = Item["result"]["signature"]

        return [signature,status]

    def CHANNEL_VERIFY(public_key,channel_id,amount,signature):
        proc = "rippled channel_verify %s" % (public_key,channel_id,amount,signature)
        output=proc.communicate()[0]
        Data = json.loads(output)

        Item = json.loads(Data)
        status = Item["result"]["status"]
        signature_verified = Item["result"]["signature_verified"]

        return [signature_verified,status]

    def CONNECT(ip,port):
        proc = "rippled connect %s %s" % (ip,port)
        output=proc.communicate()[0]
        Data = json.loads(output)

        Item = json.loads(Data)
        message = Item["result"]["message"]
        status = Item["result"]["status"]

        return [message,status]




#
