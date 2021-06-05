
#https://xrpl.org/data-api.html
import requests
import json
import csv
import os
import sys
import subprocess
import re

class Command_Control_Outputs:

    def OUTPUTS(self,Input,Command_Data):

        if Input == "consensus_info":
            consensus_info = Command_Control_Outputs.CONSENSUS_INFO(Command_Data)
            return consensus_info

        elif Input == "get_counts":
            get_counts = Command_Control_Outputs.GET_COUNTS(Command_Data)
            return get_counts

        elif Input == "ledger_accept":
            ledger_accept = Command_Control_Outputs.LEDGER_ACCEPT(Command_Data)
            return ledger_accept

        elif Input == "ledger_cleaner":
            ledger_cleaner = Command_Control_Outputs.LEDGER_CLEANER(Command_Data)
            return ledger_cleaner

        elif Input == "ledger_closed":
            ledger_closed = Command_Control_Outputs.LEDGER_CLOSED(Command_Data)
            return ledger_closed

        elif Input == "ledger_current":
            ledger_current = Command_Control_Outputs.LEDGER_CURRENT(Command_Data)
            return ledger_current

        elif Input == "logrotate":
            logrotate = Command_Control_Outputs.LOGROTATE(Command_Data)
            return logrotate

        elif Input == "peers":
            peers = Command_Control_Outputs.PEERS(Command_Data)
            return peers

        elif Input == "ping":
            ping = Command_Control_Outputs.PING(Command_Data)
            return ping

        elif Input == "random":
            random = Command_Control_Outputs.RANDOM(Command_Data)
            return random

        elif Input == "peer_reservations_list":
            peer_reservations_list = Command_Control_Outputs.PEER_RESERVATION_LIST(Command_Data)
            return peer_reservations_list

        elif Input == "server_info":
            server_info = Command_Control_Outputs.SERVER_INFO(Command_Data)
            return server_info

        elif Input == "server_state":
            server_state = Command_Control_Outputs.SERVER_STATE(Command_Data)
            return server_state

        elif Input == "stop":
            stop = Command_Control_Outputs.STOP(Command_Data)
            return stop

        elif Input == "validation_create":
            validation_create = Command_Control_Outputs.VALIDATION_CREATE(Command_Data)
            return validation_create

        elif Input == "validator_list_sites":
            validator_list_sites = Command_Control_Outputs.VALIDATOR_LIST_SITES(Command_Data)
            return validator_list_sites

        elif Input == "version":
            version = Command_Control_Outputs.VERSION(Command_Data)
            return version

        elif Input == "wallet_propose":
            wallet_propose =Command_Control_Outputs.WALLET_PROPOSE(Command_Data)
            return wallet_propose

        elif Input == "fetch_info":
            fetch_info = Command_Control_Outputs.FETCH_INFO(Command_Data)

        else:
            print("[ %s ] is an Invalid Command" % Input)


    def FETCH_INFO(DATA):
        return DATA

    def CONSENSUS_INFO(DATA): #JSON
        return DATA

    def GET_COUNTS(DATA): #JSON
        return DATA

 ########################## #TEST On Ledger !!!!!!!!!!
    def LEDGER_ACCEPT(Item): #TEST On Ledger !!!!!!!!!!
        try:
            id = Item["id"]
            status = Item["status"]
            type = Item["type"]
            ledger_current_index = Item["result"]["ledger_current_index"]
            return [id,status,type,ledger_current_index]

        except:
            return("Error connecting to Ledger")

    def LEDGER_CLEANER(DATA): 
        print("test")

    def LEDGER_CLOSED(DATA):
        print(DATA)
        Item = json.loads(DATA)

        ledger_hash = Item["result"]["ledger_hash"]
        ledger_index = Item["result"]["ledger_index"]
        status = Item["result"]["status"]
        return [ledger_hash,ledger_index,status]

    def LEDGER_CURRENT(DATA):
        print(DATA)
        Item = json.loads(DATA)

        ledger_current_index = Item["result"]["ledger_current_index"]
        status = Item["result"]["status"]
        return [ledger_current_index,status]

    def LOGROTATE(DATA): #VAR
        Item = json.loads(DATA)
        message = Item["result"]["message"]
        status = Item["result"]["status"]
        return [message,status]

    def PEERS(DATA): #VAR
        Item = json.loads(DATA)
        peers = Item["result"]["peers"]
        return peers

    def PING(DATA): #VAR
        Item = json.loads(DATA)
        role = Item["result"]["role"]
        status = Item["result"]["status"]
        return [role,status]

    def RANDOM(DATA): #VAR
        Item = json.loads(DATA)
        random = Item["result"]["random"]
        status = Item["result"]["status"]
        return [random,status]

    def PEER_RESERVATION_LIST(DATA): #VAR
        Item = json.loads(DATA)
        reservations = Item["result"]["reservations"]
        status = Item["result"]["status"]
        return [reservations,status]

    def SERVER_INFO(DATA):
        return DATA

    def SERVER_STATE(DATA):
        return DATA

    def STOP(DATA): #VARS
        Item = json.loads(DATA)
        message = Item["result"]["message"]
        status = Item["result"]["status"]
        return [message,status]

    def VALIDATION_CREATE(DATA): #VARS
        Item = json.loads(DATA)
        status = Item["result"]["status"]
        validation_key = Item["result"]["validation_key"]
        validation_public_key = Item["result"]["validation_public_key"]
        validation_seed = Item["result"]["validation_seed"]
        return [status,validation_key,validation_public_key,validation_seed]

    def VALIDATOR_LIST_SITES(DATA): #VAR
        Item = json.loads(DATA)
        validator_sites = Item["result"]["validator_sites"]
        status = Item["result"]["status"]
        return [validator_sites,status]

    def VERSION(DATA): #VAR
        Item = json.loads(DATA)
        first = Item["result"]["version"]["first"]
        good = Item["result"]["version"]["good"]
        last = Item["result"]["version"]["last"]
        status = Item["result"]["status"]
        return [first,good,last,status]

    def WALLET_PROPOSE(DATA): #VARS
        Item = json.loads(DATA)

        account_id = Item["result"]["account_id"]
        key_type = Item["result"]["key_type"]
        master_key = Item["result"]["master_key"]
        master_seed = Item["result"]["master_seed"]
        master_seed_hex = Item["result"]["master_seed_hex"]
        public_key = Item["result"]["public_key"]
        public_key_hex = Item["result"]["public_key_hex"]
        status = Item["result"]["status"]

        #print(Data)
        return [account_id,key_type,master_key,master_seed,master_seed_hex,public_key,public_key_hex,status]


class Format_Json: #REVIEW

    def GET_COUNTS(DATA):
        Item = json.load(DATA)

        AL_hit_rate = Item["result"]["AL_hit_rate"]
        HashRouterEntry = Item["result"]["HashRouterEntry"]
        Ledger = Item["result"]["Ledger"]
        NodeObject = Item["result"]["NodeObject"]
        SLE_hit_rate = Item["result"]["SLE_hit_rate"]
        STArray = Item["result"]["STArray"]
        STLedgerEntry = Item["result"]["STLedgerEntry"]
        STObject = Item["result"]["STObject"]
        STTx = Item["result"]["STTx"]
        STValidation = Item["result"]["STValidation"]
        Transaction = Item["result"]["Transaction"]
        dbKBLedger = Item["result"]["dbKBLedger"]
        dbKBTotal = Item["result"]["dbKBTotal"]
        dbKBTransaction = Item["result"]["dbKBTransaction"]
        fullbelow_size = Item["result"]["fullbelow_size"]
        historical_perminute = Item["result"]["historical_perminute"]
        ledger_hit_rate = Item["result"]["ledger_hit_rate"]
        node_hit_rate =  Item["result"]["node_hit_rate"]
        node_read_bytes = Item["result"]["node_read_bytes"]
        node_reads_hit = Item["result"]["node_reads_hit"]
        node_reads_total = Item["result"]["node_reads_total"]
        node_writes = Item["result"]["node_writes"]
        node_written_bytes = Item["result"]["node_written_bytes"]
        status = Item["result"]["status"]
        treenode_cache_size = Item["result"]["treenode_cache_size"]
        treenode_track_size = Item["result"]["treenode_track_size"]
        uptime = Item["result"]["uptime"]
        write_load = Item["result"]["write_load"]

        return [AL_hit_rate,HashRouterEntry,Ledger,NodeObject,SLE_hit_rate,STArray,STLedgerEntry,STObject,
                STTx,STValidation,Transaction,dbKBLedger,dbKBTotal,dbKBTransaction,fullbelow_size,historical_perminute,
                ledger_hit_rate,node_hit_rate,node_read_bytes,node_reads_hit,node_reads_total,node_writes,node_written_bytes,
                status,treenode_cache_size,treenode_track_size,uptime,write_load]

    def SERVER_STATE_FORMAT(DATA):
        Item = json.load(DATA)

        build_version = Item["result"]["state"]["build_version"]
        complete_ledgers = Item["result"]["state"]["complete_ledgers"]
        io_latency_ms = Item["result"]["state"]["io_latency_ms"]
        jq_trans_overflow = Item["result"]["state"]["jq_trans_overflow"]
        last_close_converge_time = Item["result"]["state"]["last_close"]["converge_time"]
        last_close_proposers = Item["result"]["state"]["last_close"]["proposers"]
        load = Item["result"]["state"]["load"]
        load_base = Item["result"]["state"]["load_base"]
        load_factor = Item["result"]["state"]["load_factor"]
        load_factor_fee_escalation = Item["result"]["state"]["load_factor_fee_escalation"]
        load_factor_fee_queue = Item["result"]["state"]["load_factor_fee_queue"]
        load_factor_fee_reference = Item["result"]["state"]["load_factor_fee_reference"]
        load_factor_server = Item["result"]["state"]["load_factor_server"]
        peer_disconnects = Item["result"]["state"]["peer_disconnects"]
        peer_disconnects_resources = Item["result"]["state"]["peer_disconnects_resources"]
        peers = Item["result"]["state"]["peers"]
        pubkey_node = Item["result"]["state"]["pubkey_node"]
        pubkey_validator = Item["result"]["state"]["pubkey_validator"]
        server_state = Item["result"]["state"]["server_state"]
        server_state_duration_us = Item["result"]["state"]["server_state_duration_us"]
        state_accounting = Item["result"]["state"]["state_accounting"]
        time = Item["result"]["state"]["time"]
        uptime = Item["result"]["state"]["uptime"]
        validated_ledger = Item["result"]["state"]["validated_ledger"]
        validation_quorum = Item["result"]["state"]["validation_quorum"]
        validator_list_expires = Item["result"]["state"]["validator_list_expires"]

        return [build_version,complete_ledgers,io_latency_ms,jq_trans_overflow,last_close_converge_time,last_close_proposers,
                load,load_base,load_factor,load_factor_fee_escalation,load_factor_fee_queue,load_factor_fee_reference,load_factor_server,
                peer_disconnects,peer_disconnects_resources,peers,pubkey_node,pubkey_validator,server_state,server_state_duration_us,
                state_accounting,time,uptime,validated_ledger,validation_quorum,validator_list_expires]

    def SERVER_INFO_FORMAT(DATA):
        Item = json.loads(DATA)

        build_version = Item["result"]["info"]["build_version"]
        complete_ledgers = Item["result"]["info"]["complete_ledgers"]
        hostid = Item["result"]["info"]["hostid"]
        io_latency_ms = Item["result"]["info"]["io_latency_ms"]
        jq_trans_overflow = Item["result"]["info"]["jq_trans_overflow"]
        last_close_converge_time_s = Item["result"]["info"]["last_close"]["converge_time_s"]
        last_close_proposers = Item["result"]["info"]["last_close"]["proposers"]
        load = Item["result"]["info"]["load"]
        load_factor = Item["result"]["info"]["load_factor"]
        peer_disconnects = Item["result"]["info"]["peer_disconnects"]
        peer_disconnects_resources = Item["result"]["info"]["peer_disconnects_resources"]
        peers = Item["result"]["info"]["peers"]
        pubkey_node = Item["result"]["info"]["pubkey_node"]
        pubkey_validator = Item["result"]["info"]["pubkey_validator"]
        server_state = Item["result"]["info"]["server_state"]
        server_state_duration_us = Item["result"]["info"]["server_state_duration_us"]
        state_accounting = Item["result"]["info"]["state_accounting"]
        time = Item["result"]["info"]["time"]
        uptime = Item["result"]["info"]["uptime"]
        validated_ledger = Item["result"]["info"]["validated_ledger"]
        validation_quorum = Item["result"]["info"]["validation_quorum"]
        validator_list = Item["result"]["info"]["validator_list"]

        return [build_version,complete_ledgers,hostid,io_latency_ms,jq_trans_overflow,last_close_converge_time_s,
                last_close_proposers,load,load_factor,peer_disconnects,peer_disconnects_resources,peers,pubkey_node,
                pubkey_validator,server_state,server_state_duration_us,state_accounting,time,uptime,validated_ledger,
                validation_quorum,validator_list]
