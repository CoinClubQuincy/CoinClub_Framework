#https://xrpl.org/data-api.html
import requests
import json
import csv
import os
import sys
import subprocess
import re

#from Transaction_Types import ErrorHandeling
from Transaction_Types import Transaction_Types
from Transaction_Types import Transaction_Types_Format_Output
from Command_Control_Outputs import Command_Control_Outputs

# rg5W75cDeaooC99xoJJeV9eV6U63u4GTX
Command_Control_Outputs = Command_Control_Outputs()

class XRP_Node_Commands:

    #wallet_propose
    def WALLET_GENERATOR_MANUAL(passphrase):
        print("Generating Keys")
        DATA = 'rippled wallet_propose %s' % passphrase
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]
        Data = json.loads(output)

        account_id = Data["result"]["account_id"]
        key_type = Data["result"]["key_type"]
        master_key = Data["result"]["master_key"]
        master_seed = Data["result"]["master_seed"]
        master_seed_hex = Data["result"]["master_seed_hex"]
        public_key = Data["result"]["public_key"]
        public_key_hex = Data["result"]["public_key_hex"]
        status = Data["result"]["status"]

        #print(Data)
        return [account_id,key_type,master_key,master_seed,master_seed_hex,public_key,public_key_hex,status]


        #Simple Node Commands [consensus_info,get_counts,ledger_accept,ledger_cleaner,
        #                      ledger_closed,ledger_current,logrotate,peers,ping,random,
        #                      peer_reservations_list,server_info,server_state,stop,
        #                      validation_create,validator_list_sites,version,wallet_propose]

    # validation_create
    def VALIDATION_CREATE_MANUAL(passphrase):
        DATA = 'rippled validation_create %s' % passphrase
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]
        Item = json.loads(output)

        status = Item["result"]["status"]
        validation_key = Item["result"]["validation_key"]
        validation_public_key = Item["result"]["validation_public_key"]
        validation_seed = Item["result"]["validation_seed"]

        return [status,validation_key,validation_public_key,validation_seed]

    def COMAND_CONTROL(CLI_command):
        DATA = 'rippled %s' % CLI_command
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]

        Data = Command_Control_Outputs.OUTPUTS(CLI_command,output)
        return Data

#REVIEW
###################### EXPERIMENTAL [TEST BEFORE BUILDING ON TOP OF] ######################

        #submit
    def SUBMIT(Type,submit_hash): # Type = [Submit-only,Sign-and-submit]
        if Type == "Submit-only":
            proc = "rippled submit %s" % submit_hash
            output=proc.communicate()[0]
            Data = json.loads(output)
            return Data

        elif Type == "Sign-and-submit":
            proc = "rippled submit %s" % TransactionType
            output=proc.communicate()[0]
            Data = json.loads(output)
            return Data
        else:
            print("Error: Options: Submit-only | Options: Sign-and-submit")


    def SUBMIT_MULTISIGNED(submit_hash):
        proc = "rippled submit_multisigned %s" % submit_hash
        output=proc.communicate()[0]
        Data = json.loads(output)
        print(Data)

    #sign
    def SIGN(secret_key,TransactionType):
        proc = "rippled sign %s %s" % (secret_key,TransactionType)
        output=proc.communicate()[0]
        Data = json.loads(output)
        print(Data)


    #sign_for
    def SIGN_FOR(sign_for_addy,secret_key,TransactionType):
        proc = "rippled sign_for %s %s" % (secret_key,TransactionType)
        output=proc.communicate()[0]
        Data = json.loads(output)
        print(Data)
#REVIEW
###################### ###################### ###################### ######################

        #ledger_request
    def LEDGER_REQUEST(ledger):
        DATA = "rippled ledger_request %s" % ledger
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]

        return output


    def GATEWAY_BALANCE(account):
        DATA = "rippled gateway_balances %s" % account
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]
        Data = json.loads(output)
        return Data
        #after test return data


    def DEPOSIT_AUTHORIZED(source_account,destination_account):
        DATA = 'rippled deposit_authorized %s %s' % (source_account,destination_account)
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]
        Item = json.loads(output)

        deposit_authorized = Item["result"]["deposit_authorized"]
        destination_account = Item["result"]["destination_account"]
        ledger_index = Item["result"]["ledger_current_index"]
        source_account = Item["result"]["source_account"]
        status = Item["result"]["status"]
        validated = Item["result"]["validated"]

        return [deposit_authorized,destination_account,ledger_index,source_account,status,validated]

    def DOWNLOAD_SHARD(index,url):
        DATA = 'rippled download_shard %s %s ' % (index,url)
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]
        Item = json.loads(output)

        message = Item["result"]["message"]
        status = Item["result"]["status"]

        return [message,status]

    def FEATURE(id=""):
        DATA = 'rippled feature %s' % id
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]
        Item = json.loads(output)

        if id != '':
            enabled = Item["result"][featureID]["enabled"]
            name = Item["result"][featureID]["name"]
            supported = Item["result"][featureID]["supported"]
            vetoed = Item["result"][featureID]["vetoed"]
            status = Item["result"]["status"]

            return [enabled,name,supported,vetoed,status]
        else:
            return Item

    def LOG_LEVEL(severity):
        DATA = 'rippled log_level %s ' % (severity)
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]

        return output

    def PEER_RESERVATIONS_ADD(pubkey,description):
        DATA = 'rippled log_level %s %s ' % (pubkey,description)
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]
        Item = json.loads(output)

        description = Item["result"]["previous"]["description"]
        node = Item["result"]["previous"]["node"]
        status = Item["result"]["status"]

        return [node,description,status]


    def PEER_RESERVATIONS_DEL(pubkey):
        DATA = 'rippled log_level %s' % (pubkey)
        proc=subprocess.Popen(DATA , shell=True, stdout=subprocess.PIPE, )
        output=proc.communicate()[0]
        Item = json.loads(output)

        description = Item["result"]["previous"]["description"]
        node = Item["result"]["previous"]["node"]
        status = Item["result"]["status"]

        return [node,description,status]

    def RIPPLE_PATH_FIND(json):
        proc = "rippled ripple_path_find %s" % (json)
        output=proc.communicate()[0]
        Data = json.loads(output)

        Item = json.loads(Data)
        alternatives = Item["result"]["alternatives"]
        destination_account = Item["result"]["destination_account"]
        destination_amount = Item["result"]["destination_amount"]
        destination_currencies = Item["result"]["destination_currencies"]
        full_reply = Item["result"]["full_reply"]
        source_account =Item["result"]["source_account"]
        status = Item["result"]["status"]

        return [alternatives,destination_account,destination_amount,destination_currencies,
                full_reply,source_account,source_account,status]


#
