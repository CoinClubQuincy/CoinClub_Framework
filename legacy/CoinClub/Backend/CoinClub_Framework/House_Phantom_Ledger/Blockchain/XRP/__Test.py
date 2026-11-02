from Transaction_Types import Transaction_Types
from Transaction_Types import Transaction_Types_Format_Output
from Command_Control_Outputs import Command_Control_Outputs
from XRP_Node_Commands import XRP_Node_Commands
from Account_Details import Account_Details
import re
import json
import time

class Test:
    def __init__(self):
        print("---------------------------------- Start Test Func ----------------------------------")
        time.sleep(4)

        self.XRP_NODE_Commands_TEST()

        self.Account_Details_Test()

        self.Ledger_Actions()

        self.TransactionTypes()

        print("---------------------------------- All Test Func Complete!! ----------------------------------")

    def XRP_NODE_Commands_TEST(self):
        print("---------------------------------- Start  XRP_NODE_Commands_TEST ----------------------------------")
        time.sleep(5)

        print("---------------------------------- wallet_propose ----------------------------------")
        [account_id,key_type,master_key,master_seed,master_seed_hex,public_key,public_key_hex,status] = XRP_Node_Commands.COMAND_CONTROL("wallet_propose")
        print(master_key)
        time.sleep(1)

        print("---------------------------------- version ----------------------------------")
        [first,good,last,status] = XRP_Node_Commands.COMAND_CONTROL("version")
        print(good)
        time.sleep(1)

        print("---------------------------------- validator_list_sites ----------------------------------")
        [validator_sites,status] = XRP_Node_Commands.COMAND_CONTROL("validator_list_sites")
        print(validator_sites)
        time.sleep(1)

        print("---------------------------------- validation_create ----------------------------------")
        [status,validation_key,validation_public_key,validation_seed] = XRP_Node_Commands.COMAND_CONTROL("validation_create")
        print(validation_seed)
        time.sleep(1)

        print("---------------------------------- Stop ----------------------------------")
        print("skip stop in test")
        time.sleep(1)

        print("---------------------------------- server_state ----------------------------------")
        server_state = XRP_Node_Commands.COMAND_CONTROL("server_state")
        print(server_state)
        time.sleep(1)

        print("---------------------------------- server_info ----------------------------------")
        server_info = XRP_Node_Commands.COMAND_CONTROL("server_info")
        print(server_info)
        time.sleep(1)

        print("---------------------------------- peer_reservations_list ----------------------------------")
        [reservations,status] = XRP_Node_Commands.COMAND_CONTROL("peer_reservations_list")
        print(reservations)
        time.sleep(1)

        print("---------------------------------- random ----------------------------------")
        [random,status] = XRP_Node_Commands.COMAND_CONTROL("random")
        print(random)
        time.sleep(1)

        print("---------------------------------- ping ----------------------------------")
        [role,status] = XRP_Node_Commands.COMAND_CONTROL("ping")
        print(role)
        time.sleep(1)

        print("---------------------------------- peers ----------------------------------")
        peers= XRP_Node_Commands.COMAND_CONTROL("peers")
        print(peers)
        time.sleep(1)

        print("---------------------------------- logrotate ----------------------------------")
        [message,status] = XRP_Node_Commands.COMAND_CONTROL("logrotate")
        print(message)
        time.sleep(1)

        print("---------------------------------- get_counts ----------------------------------")
        get_counts = XRP_Node_Commands.COMAND_CONTROL("get_counts")
        print(get_counts)
        time.sleep(1)

        print("---------------------------------- consensus_info ----------------------------------")
        consensus_info = XRP_Node_Commands.COMAND_CONTROL("consensus_info")
        print(consensus_info)
        time.sleep(1)


        print("---------------------------------- fetch_info ----------------------------------")
        fetch_info = XRP_Node_Commands.COMAND_CONTROL("fetch_info")
        print(fetch_info)
        time.sleep(1)

        print("---------------------------------- ledger_cleaner ----------------------------------")
        ledger_cleaner = XRP_Node_Commands.COMAND_CONTROL("ledger_cleaner")
        print(ledger_cleaner)


        print("---------------------------------- ledger_closed ----------------------------------")
        ledger_closed = XRP_Node_Commands.COMAND_CONTROL("ledger_closed")
        print(ledger_closed)

        print("---------------------------------- ledger_current ----------------------------------")
        ledger_current = XRP_Node_Commands.COMAND_CONTROL("ledger_current")
        print(ledger_current)

        print("---------------------------------- ledger_accept ----------------------------------")
        #ledger_accept = XRP_Node_Commands.COMAND_CONTROL("ledger_accept")
        print("skip ledger_accept")

        print("---------------------------------- END XRP_NODE_Commands_TEST  ----------------------------------")
        time.sleep(1)

    def Ledger_Actions(self):
        print("---------------------------------- START Test Ledger_Actions ----------------------------------")
        time.sleep(1)
        addy = "rUhbURn9gPQWcjfqTip5YsMSstBfX8UV9h"

        print("---------------------------------- GATEWAY_BALANCE ----------------------------------")
        GATEWAY_BALANCE = XRP_Node_Commands.GATEWAY_BALANCE(addy)
        print(GATEWAY_BALANCE)
        time.sleep(1)


        print("---------------------------------- LOG_LEVEL ----------------------------------")
        ledger = XRP_Node_Commands.LOG_LEVEL("")
        print(ledger)
        time.sleep(1)

        print("---------------------------------- LEDGER_REQUEST ----------------------------------")
        ledger = XRP_Node_Commands.LEDGER_REQUEST("63370303")
        print(ledger)
        time.sleep(1)

        print("---------------------------------- DEPOSIT_AUTHORIZED ----------------------------------")
        [deposit_authorized,destination_account,ledger_index,source_account,status,validated] = XRP_Node_Commands.DEPOSIT_AUTHORIZED("rUhbURn9gPQWcjfqTip5YsMSstBfX8UV9h","rg5W75cDeaooC99xoJJeV9eV6U63u4GTX")
        print(status)
        time.sleep(1)

        print("---------------------------------- FEATURE ----------------------------------")
        status = XRP_Node_Commands.FEATURE()
        print(status)
        time.sleep(1)



        print("---------------------------------- END Test Ledger_Actions ----------------------------------")
        time.sleep(1)

    def Account_Details_Test(self):
        print("---------------------------------- START Account Details Test ----------------------------------")
        time.sleep(5)

        addy = "rUhbURn9gPQWcjfqTip5YsMSstBfX8UV9h"
        dest_addy = "rg5W75cDeaooC99xoJJeV9eV6U63u4GTX"
        accountID = "rg5W75cDeaooC99xoJJeV9eV6U63u4GTX"

        print("---------------------------------- ACCOUNT_CURRENCIES ----------------------------------")
        [receive_currencies,send_currencies,status,validated] = Account_Details.ACCOUNT_CURRENCIES(addy)
        print(status)
        time.sleep(1)

        print("---------------------------------- ACCOUNT_INFO ----------------------------------")
        [Account,Balance,Flags,LedgerEntryType,OwnerCount,
        PreviousTxnID,PreviousTxnLgrSeq,Sequence,
        index,ledger_index,status,validated] = Account_Details.ACCOUNT_INFO(addy)
        print(status)
        time.sleep(1)

        print("---------------------------------- ACCOUNT_LINES ----------------------------------")
        [account,ledger_current_index,lines,status,validated] = Account_Details.ACCOUNT_LINES(addy)
        print(status)
        time.sleep(1)

        print("---------------------------------- ACCOUNT_OBJECTS ----------------------------------")
        [account,account_objects,ledger_index,status,validated]= Account_Details.ACCOUNT_OBJECTS(addy)
        print(status)
        time.sleep(1)

        print("---------------------------------- ACCOUNT_OFFERS ----------------------------------")
        [account,ledger_current_index,offers,status,validated] = Account_Details.ACCOUNT_OFFERS(addy)
        print(status)
        time.sleep(1)

        print("---------------------------------- ACCOUNT_TX ----------------------------------")
        [account,ledger_index_max,ledger_index_min,limit,status,transactions,validated] = Account_Details.ACCOUNT_TX(addy)
        print(status)
        time.sleep(1)

        print("---------------------------------- ACCOUNT_CHANNELS ----------------------------------")
        [account,channels,ledger_index,status,validated]= Account_Details.ACCOUNT_CHANNELS(addy)
        print(status,channels)
        time.sleep(1)


        print("---------------------------------- BOOK_OFFERS ----------------------------------")
        [ledger_current_index,offers,status,validated] = Account_Details.BOOK_OFFERS("USD/rUhbURn9gPQWcjfqTip5YsMSstBfX8UV9h" ,"USD/rg5W75cDeaooC99xoJJeV9eV6U63u4GTX")
        print(status,channels)
        time.sleep(1)


        print("---------------------------------- END Account Details Test ----------------------------------")
        time.sleep(5)


    def TransactionTypes(self):
        print("---------------------------------- START TransactionTypes  Test ----------------------------------")
        time.sleep(1)


        print("---------------------------------- END TransactionTypes  Test ----------------------------------")
        time.sleep(1)


if "__main__" == __name__:
    Test()
