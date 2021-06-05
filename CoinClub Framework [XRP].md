#    **CoinClub** Framework **[XRP]                                             [TEST_functions & Error handeling] Python Documentation** 

######    **version 1.0.1**

###### **Project Devs:** [ R Quincy Jones ]

###### **Sources:**

- https://xrpl.org/references.html
- https://xumm.readme.io/reference/about

### **Introduction:**

Welcome to The CoinClub Python Interledger Framework for [XRP]

This Python Documentation document is broken up into 3 parts

- **CoinClub Framework [ XRP_Node_Commands ] & [ Account_Details ]** 

    - Main XRP Node commands, account management, Ledger Read commands & Signing transactions 

- **CoinClub Framework Reference  [XRP-Transaction Types]** 

    - Side Liberary for Transaction Types for XRPL

- **CoinClub Framework XUMM API Doc**

    - XUMM API [XUMM was an app built by ripple in the early Stage of XRPL]

        

##### **Basic System Requirements:**

- Mac OS & Ubuntu OS (or Docker Container)
- 2.0GHz CPU, 8GB Memory
- Python3.8 &pip3

### **Dependancies:** 

### [Set Up Rippled Node Server Mac OS] (Cant get to work)

```sh
echo "Download Ripple Node Dependencies"

export GitRepo= #Enter Git Repo Adress Name
export PWD_Boost_folder= #Enter Folder Directory

xcode-select --install
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

brew update
brew install git cmake pkg-config protobuf openssl ninja


./bootstrap.sh
./b2 cxxflags="-std=c++14"  visibility=global

#FORK code from git hub
git clone git@github.com:{Git Repo}ripple/rippled.git
cd rippled

git checkout master

export BOOST_ROOT={PWD_Boost_folder}/boost_1_70_0

mkdir my_build
cd my_build

cmake -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Debug ..

cmake --build . -- -j 4

```



### [Set Up Rippled Node Server Ubuntu16.08]  [NOT TESTED]

```sh
echo "Download Start Ripple.d Dependancies"

# [NOT TESTED]
sudo apt update
sudo apt install python3
sudo apt install python3-pip

pip3 install requests


# /etc/init.d/dbus start
#Rippled

sudo apt-get install systemd
sudo apt -y update
sudo apt -y install rippled

systemctl status rippled.service

sudo systemctl start rippled.service
sudo systemctl enable rippled.service

/opt/ripple/bin/rippled server_info

```

# [ XRP_Node_Commands ]

#### **Note:** All Output variables are Strings

#### Wallet Generator: 

```python
from XRP_Node_Commands import XRP_Node_Commands
# Output Variables listed Below in Code Details
[account_id,key_type,
 master_key,
 master_seed,
 master_seed_hex,
 public_key,
 public_key_hex,
 status] = XRP_Node_Commands.WALLET_GENERATOR_MANUAL(passphrase)

print(account_id) #will print account ID
```

###### **Code Details:**

**Description:**  

- Generate a key pair and XRP Ledger address. This command only generates 	key and address values, and does not affect the XRP Ledger itself in any way. To become a funded address stored in the ledger, the address must [receive a Payment transaction](https://xrpl.org/accounts.html#creating-accounts) that provides enough XRP to meet the [reserve requirement](https://xrpl.org/reserves.html).

**Parameters:** 

- **passphrase** ( **str()** ):

    *(Optional)* Generate a key pair and address from this seed value. This value can be formatted in [hexadecimal ](https://en.wikipedia.org/wiki/Hexadecimal), the XRP Ledger's [base58](https://xrpl.org/base58-encodings.html) format, [RFC-1751 ](https://tools.ietf.org/html/rfc1751), or as an arbitrary string. Cannot be used with `seed` or `seed_hex`.

**Output variables:**	

- **account_id,key_type,master_key,master_seed,master_seed_hex,public_key,public_key_hex,status**

#### Validation Generator:

```python
from XRP_Node_Commands import XRP_Node_Commands
# Output Variables listed Below in Code Details
[status,
 validation_key,
 validation_public_key,
 validation_seed] = XRP_Node_Commands.VALIDATION_CREATE_MANUAL(passphrase)

print(validation_public_key) # prints variable
```

###### **Code Details:**

**Description:** 

- generate [cryptographic keys a `rippled` server can use to identify itself to the network](https://xrpl.org/peer-protocol.html#node-key-pair). Similar to the [wallet_propose method](https://xrpl.org/wallet_propose.html), this method only generates a set of keys in the proper format. It does not any makes changes to the XRP Ledger data or server configuration.

**Parameters:** 

- **passphrase** ( **str()** ): 

    *(Optional)* Generate a key pair and address from this seed value. This value can be formatted in [hexadecimal ](https://en.wikipedia.org/wiki/Hexadecimal), the XRP Ledger's [base58](https://xrpl.org/base58-encodings.html) format, [RFC-1751 ](https://tools.ietf.org/html/rfc1751), or as an arbitrary string. Cannot be used with `seed` or `seed_hex`.

**Output variables**:	

- **status,validation_key,validation_public_key,validation_seed**

#### Comand Control & Outputs:[NOT TESTED]

```python
#CLI_Comands Functions & Outputs: 
# Look up functionality on https://xrpl.org/

#consensus_info = JSON [json.loads(JSON)]
#get_counts = JSON [json.loads(JSON)]
#ledger_accept = id,status,type,ledger_current_index
#ledger_cleaner = JSON [TMP][json.loads(JSON)]
#ledger_closed = ledger_hash,ledger_index,status
#ledger_current = ledger_current_index,status
#logrotate = message,status
#peers = JSON [json.loads(JSON)]
#ping = role,status
#random = random,status
#peer_reservations_list =  reservations,status
#server_info = JSON [json.loads(JSON)]
#server_state = JSON [json.loads(JSON)]
#stop = message,status
#validation_create=status,validation_key,validation_public_key,validation_seed

#validator_list_sites = validator_sites,status
#version = first,good,last,status
#wallet_propose=account_id,key_type,master_key,master_seed,master_seed_hex,public_key,public_key_hex,status
```
```python
from XRP_Node_Commands import XRP_Node_Commands
# Output Variables listed Below in Code Details
Output_variables = [] # output variables above can be used to activate function
Output_variables = XRP_Node_Commands.COMAND_CONTROL(CLI_command)
print(Output_variables)
```

###### **Code Details:**

**Description:**

- This is the description

**Parameters:** 

- **CLI_command** ( **str()** ): Enter A command Control command

- Basic Node read commands for control over Rippled Node and DLT 

- Most command have multiple variable outputs

- If not a variabled output, funtion by default will read data as json

###### JSON Variable options 

**Description:** These commands need **Format_Json** class to convert JSON into variables

- GET_COUNTS(DATA)
- SERVER_INFO(DATA)
- SERVER_STATE(DATA)

```python

#[X] get_counts = AL_hit_rate,HashRouterEntry,Ledger,NodeObject,SLE_hit_rate,STArray,STLedgerEntry,STObject,STTx,STValidation,Transaction,dbKBLedger,dbKBTotal,dbKBTransaction,fullbelow_size,historical_perminute,ledger_hit_rate,node_hit_rate,node_read_bytes,node_reads_hit,node_reads_total,node_writes,node_written_bytes,status,treenode_cache_size,treenode_track_size,uptime,write_load

#[X] server_state_format = build_version,complete_ledgers,io_latency_ms,jq_trans_overflow,last_close_converge_time,last_close_proposers,load,load_base,load_factor,load_factor_fee_escalation,load_factor_fee_queue,load_factor_fee_reference,load_factor_server,peer_disconnects,peer_disconnects_resources,peers,pubkey_node,pubkey_validator,server_state,server_state_duration_us,state_accounting,time,uptime,validated_ledger,validation_quorum,validator_list_expires

#[X] server_info_format = build_version,complete_ledgers,hostid,io_latency_ms,jq_trans_overflow,last_close_converge_time_s,last_close_proposers,load,load_factor,peer_disconnects,peer_disconnects_resources,peers,pubkey_node,pubkey_validator,server_state,server_state_duration_us,state_accounting,time,uptime,validated_ledger,validation_quorum,validator_list
```

```python
# Example Using (server_info_format):
from XRP_Node_Commands import XRP_Node_Commands
from Command_Control_Outputs import Format_Json

Output = XRP_Node_Commands.COMAND_CONTROL("server_info_format")

[build_version,complete_ledgers,hostid,io_latency_ms,
 jq_trans_overflow,last_close_converge_time_s,
 last_close_proposers,load,load_factor,peer_disconnects,
 peer_disconnects_resources,peers,pubkey_node,
 pubkey_validator,server_state,server_state_duration_us,
 state_accounting,time,uptime,validated_ledger,
 validation_quorum,
 validator_list] = Format_Json.SERVER_STATE_FORMAT(Output)
```



### **Comand Details:**

| *<u>Command</u>*           | *<u>Description</u>*                                         |
| -------------------------- | ------------------------------------------------------------ |
| **consensus_info**         | The XRP Ledger has a new ledger version every several seconds. When the network agrees on the contents of a ledger version, that ledger version is *validated*, and its contents can never change. The validated ledger versions that preceded it form the ledger history. Even the most recent validated ledger is part of history, as it represents the state of the network as of a short time ago. In the present, the network is evaluating transactions which may be applied and finalized in the next ledger version. While this evaluation is happening, the network has candidate ledger versions that are not yet validated. |
| **get_counts**             | The `get_counts` command provides various stats about the health of the server, mostly the number of objects of different types that it currently holds in memory. |
| **ledger_accept**          | The `ledger_accept` method forces the server to close the current-working ledger and move to the next ledger number. This method is intended for testing purposes only, and is only available when the `rippled` server is running stand-alone mode. *The `ledger_accept` method is an [admin method](https://xrpl.org/admin-rippled-methods.html) that cannot be run by unprivileged users!* |
| **ledger_cleaner**         | The `ledger_cleaner` command controls the [Ledger Cleaner ](https://github.com/ripple/rippled/blob/f313caaa73b0ac89e793195dcc2a5001786f916f/src/ripple/app/ledger/README.md#the-ledger-cleaner), an asynchronous maintenance process that can find and repair corruption in `rippled`'s database of ledgers. *The `ledger_cleaner` method is an [admin method](https://xrpl.org/admin-rippled-methods.html) that cannot be run by unprivileged users.* |
| **ledger_closed**          | The `ledger_closed` method returns the unique identifiers of the most recently closed ledger. (This ledger is not necessarily validated and immutable yet.) |
| **ledger_current**         | The `ledger_current` method returns the unique identifiers of the current in-progress [ledger](https://xrpl.org/ledgers.html). This command is mostly useful for testing, because the ledger returned is still in flux. |
| **logrotate**              | The `logrotate` command closes and reopens the log file. This is intended to help with log rotation on Linux file systems. |
| **peers**                  | The `peers` command returns a list of all other `rippled` servers currently connected to this one over the [Peer Protocol](https://xrpl.org/peer-protocol.html), including information on their connection and sync status. *The `peers` method is an [admin method](https://xrpl.org/admin-rippled-methods.html) that cannot be run by unprivileged users!* |
| **ping**                   | The `ping` command returns an acknowledgement, so that clients can test the connection status and latency. |
| **random**                 | The `random` command provides a random number to be used as a source of entropy for random number generation by clients. |
| **peer_reservations_list** | Normally, a `rippled` server attempts to maintain a healthy number of peers, and automatically connects to untrusted peers up to a maximum number. You can configure a `rippled` server to remain connected to specific peer servers in several ways: *The `peer_reservations_list` method is an [admin method](https://xrpl.org/admin-rippled-methods.html) that cannot be run by unprivileged users.* |
| **server_info**            | The `server_info` command asks the server for a human-readable version of various information about the `rippled` server being queried. |
| **server_state**           | The `server_state` command asks the server for various machine-readable information about the `rippled` server's current state. The response is almost the same as the [server_info method](https://xrpl.org/server_info.html), but uses units that are easier to process instead of easier to read. (For example, XRP values are given in integer drops instead of scientific notation or decimal values, and time is given in milliseconds instead of seconds.) |
| **stop**                   | Gracefully shuts down the server. *The `stop` method is an [admin method](https://xrpl.org/admin-rippled-methods.html) that cannot be run by unprivileged users!* |
| **validation_create**      | Use the `validation_create` command to generate [cryptographic keys a `rippled` server can use to identify itself to the network](https://xrpl.org/peer-protocol.html#node-key-pair). Similar to the [wallet_propose method](https://xrpl.org/wallet_propose.html), this method only generates a set of keys in the proper format. It does not any makes changes to the XRP Ledger data or server configuration. **You can configure your server to use the generated key pair to sign validations (validation key pair) or regular peer-to-peer communications ([node key pair](https://xrpl.org/peer-protocol.html#node-key-pair))**. *The `validation_create` method is an [admin method](https://xrpl.org/admin-rippled-methods.html) that cannot be run by unprivileged users.* |
| **validator_list_sites**   | The `validator_list_sites` command returns status information of sites serving validator lists *The `validator_list_sites` method is an [admin method](https://xrpl.org/admin-rippled-methods.html) that cannot be run by unprivileged users!* |
| **version**                | prints latest rippled version                                |
| **wallet_propose**         | Use the `wallet_propose` method to generate a key pair and XRP Ledger address. This command only generates key and address values, and does not affect the XRP Ledger itself in any way. To become a funded address stored in the ledger, the address must [receive a Payment transaction](https://xrpl.org/accounts.html#creating-accounts) that provides enough XRP to meet the [reserve requirement](https://xrpl.org/reserves.html).*The `wallet_propose` method is an [admin method](https://xrpl.org/admin-rippled-methods.html) that cannot be run by unprivileged users!* (This command is restricted to protect against people sniffing network traffic for account secrets, since admin commands are not usually transmitted over the outside network.) |
|                            |                                                              |



#### Submit & Sign [ALL] [NOT TESTED]

- #### **TransactionType Syntax in CoinClub Framework Reference Page**

###### Submit

```python
			#------------------------------Examples------------------------------#
from XRP_Node_Commands import XRP_Node_Commands
from TransactionType import TransactionType
from Transaction_Types import Transaction_Types_Format_Output

TT = TransactionType()
TT_FO = Transaction_Types_Format_Output()

#transaction Type will decide what type of transaction and needs to be established first, this is the TransactionType there are many to choose from
Submit_TransactionType = TT.CHECK_CASH(Account,Amount,CheckID,Fee)# TransactionType Example

# Submit will execute function   
#[  Type: [Submit-only,Sign-and-submit]    ]
submit = XRP_Node_Commands.SUBMIT(Type,Submit_TransactionType)
print(submit) # print json Output


#will return indipendant variables
# Output Variables listed Below in Code Details
TT_FO.SUBMIT(submit)
```

###### **Code Details:**

**Description:**

- The `submit` method applies a [transaction](https://xrpl.org/transaction-formats.html) and sends it to the network to be confirmed and included in future ledgers.To send a transaction as robustly as possible, you should construct and [sign](https://xrpl.org/sign.html) it in advance, persist it somewhere that you can access even after a power outage, then `submit` it as a `tx_blob`. After submission, monitor the network with the [tx method](https://xrpl.org/tx.html) command to see if the transaction was successfully applied; if a restart or other problem occurs, you can safely re-submit the `tx_blob` transaction: it won't be applied twice since it has the same sequence number as the old transaction.

 This command has two modes:

- **Submit-only** mode takes a signed, serialized transaction as a binary blob, and submits it to the network as-is. Since signed transaction objects are immutable, no part of the transaction can be modified or automatically filled in after submission.
- **Sign-and-submit** mode takes a JSON-formatted Transaction object, completes and signs the transaction in the same manner as the [sign method](https://xrpl.org/sign.html), and then submits the signed transaction. We recommend only using this mode for testing and development.

**Parameters:** 

- **Submit_TransactionType**: Select TransactionType for Submit transaction

**Example** **Output variables:** 

- **accepted,account_sequence_available,account_sequence_next,applied,
    broadcast,engine_result,engine_result_code,engine_result_message,status,kept,open_ledger_cost,queued,tx_blob,Account,currency,issuer,value,Destination,Fee,Flags,Sequence,SigningPubKey,TransactionType,TxnSignature,hash,validated_ledger_index**

##### **Output variables Code**

```python
from Transaction_Types import Transaction_Types_Format_Output
from XRP_Node_Commands import XRP_Node_Commands

TT_FO = Transaction_Types_Format_Output()
#SUBMIT ------------------------------------------------------------------------
submit_output = XRP_Node_Commands.SUBMIT(Type,TransactionType)

# Output Vars:
[accepted,account_sequence_available,account_sequence_next,applied,
 broadcast,engine_result,engine_result_code,engine_result_message,
 status,kept,open_ledger_cost,queued,tx_blob,Account,currency,issuer,value,
 Destination,Fee,Flags,Sequence,SigningPubKey,TransactionType,TxnSignature,
 hash,validated_ledger_index] = TT_FO.SUBMIT(submit_output)

```

------



###### Submit Multisigned 

###### [INCOMPLETE!!!] [Outputs]

###### **Code Details:**

**Description:**

-  The `submit_multisigned` command applies a [multi-signed](https://xrpl.org/multi-signing.html) transaction and sends it to the network to be included in future ledgers. (You can also submit multi-signed transactions in binary form using the [`submit` command in submit-only mode](https://xrpl.org/submit.html#submit-only-mode).) This command requires the [MultiSign amendment](https://xrpl.org/known-amendments.html#multisign) to be enabled. This command requires the [MultiSign amendment](https://xrpl.org/known-amendments.html#multisign) to be enabled.
- A successful SignerListSet transaction replaces the account's [`SignerList` object](https://xrpl.org/signerlist.html) in the ledger, or adds one if it did not exist before. An account may not have more than one signer list. To delete a signer list, you must set `SignerQuorum` to `0` *and* omit the `SignerEntries` field. Otherwise, the transaction fails with the error [`temMALFORMED`](https://xrpl.org/tem-codes.html). A transaction to delete a signer list is considered successful even if there was no signer list to delete.
- You cannot create a signer list such that the `SignerQuorum` could never be met. The `SignerQuorum` must be greater than 0 but less than or equal to the sum of the `SignerWeight` values in the list. Otherwise, the transaction fails with the error [`temMALFORMED`](https://xrpl.org/tem-codes.html).
- You can create, update, or remove a signer list using the master key, regular key, or the current signer list, if those methods of signing transactions are available.
- You cannot remove the last method of signing transactions from an account. If an account's master key is disabled (the account has the [`lsfDisableMaster` flag](https://xrpl.org/accountroot.html#accountroot-flags) enabled) and the account does not have a [Regular Key](https://xrpl.org/cryptographic-keys.html) configured, then you cannot delete the signer list from the account. Instead, the transaction fails with the error [`tecNO_ALTERNATIVE_KEY`](https://xrpl.org/tec-codes.html).
- With the [MultiSignReserve amendment](https://xrpl.org/known-amendments.html#multisignreserve) enabled, creating or replacing a signer list enables the `lsfOneOwnerCount` flag on the [SignerList object](https://xrpl.org/signerlist.html). When this flag is enabled, the XRP Ledger is able to lower the [`OwnerCount`](https://xrpl.org/accountroot.html#accountroot-fields) and [owner reserve](https://xrpl.org/reserves.html#owner-reserves) for the signer list. For more information, see [SignerList Flags](https://xrpl.org/signerlist.html#signerlist-flags).

**Parameters:** 

- **Account**
- **Fee**
- **Flags**
- **LimitAmount_currency**
- **LimitAmount_issuer**
- **LimitAmount_value**
- **Sequence**
- **Signer_Account1**
- **Signer_SigningPubKey1**
- **SignerTxnSignature1**
- **Signer_Account2**
- **Signer_SigningPubKey2**
- **SignerTxnSignature2**
- **SigningPubKey**
- **TransactionType**
- **hash**

**Output variables:**

- **[Test]**

#####  

------

###### Sign 

```python
from XRP_Node_Commands import XRP_Node_Commands
from TransactionType import TransactionType
from Transaction_Types import Transaction_Types_Format_Output

TT = TransactionType()
TT_FO = Transaction_Types_Format_Output()

#transaction Type will decide what type of transaction and needs to be established first	#this is the TransactionType there are many to choose from
SignTransactionType = TT.CHECK_CASH(Account,Amount,CheckID,Fee)# TransactionType Example

#Sign will execute function
Sign = XRP_Node_Commands.SIGN(SignTransactionType)

#Assign output variables
# Output Variables listed Below in Code Details
TT_FO.SIGN(Sign) 
```

###### **Code Details:**

**Description:** 

- The `sign` method takes a [transaction in JSON format](https://xrpl.org/transaction-formats.html) and a [seed value](https://xrpl.org/cryptographic-keys.html), and returns a signed binary representation of the transaction. To contribute one signature to a [multi-signed transaction](https://xrpl.org/multi-signing.html), use the [sign_for method](https://xrpl.org/sign_for.html) instead.

**Parameters:** 

- **SignTransactionType**: Select TransactionType for Sign transaction

**Output variables:** 

- **status,tx_blob,Account,currency,issuer,value,Destination,Fee,Flags,Sequence,SigningPubKey,TransactionType,TxnSignature,hash**

##### **Output variables Code**

```python
from Transaction_Types import Transaction_Types_Format_Output
from XRP_Node_Commands import XRP_Node_Commands

TT_FO = Transaction_Types_Format_Output
#SIGN --------------------------------------------------------------------------
Sign_output = XRP_Node_Commands.SIGN(TransactionType)

# Output Vars:
status,tx_blob,Account,currency,issuer,value,Destination,
Fee,Flags,Sequence,SigningPubKey,TransactionType,
TxnSignature,hash = TT_FO.SIGN(Sign_output)
```

------

###### Sign For

```python
from XRP_Node_Commands import XRP_Node_Commands
from TransactionType import TransactionType
from Transaction_Types import Transaction_Types_Format_Output

TT = TransactionType()
TT_FO = Transaction_Types_Format_Output()

#transaction Type will decide what type of transaction and needs to be established first
SignFor_TransactionType = TT.CHECK_CASH(Account,Amount,CheckID,Fee)# TransactionType Example

#Sign for will execute function
Sign_for = XRP_Node_Commands.SIGN_FOR(SignFor_TransactionType)

# Assign output variables
# Output Variables listed Below in Code Details
TT_FO.SIGN_FOR(Sign_for)
```

###### **Code Details:**

**Description:** 

- The `sign_for` command provides one signature for a [multi-signed transaction](https://xrpl.org/multi-signing.html). This command requires the [MultiSign amendment](https://xrpl.org/known-amendments.html#multisign) to be enabled. 

**Parameters:** 

- **Sign_ForTransactionType**: Select TransactionType for Sign_For transaction

**Output variables:** 

- **stats,tx_blob,Account,Fee,Flags,currency,issuer,value,Sequence,signer_Account,SigningPubKey,TransactionType,hash**

##### **Output variables Code**

```python
from Transaction_Types import Transaction_Types_Format_Output
from XRP_Node_Commands import XRP_Node_Commands

TT_FO = Transaction_Types_Format_Output()

#SIGN_FOR ----------------------------------------------------------------------
Sign_for_output = XRP_Node_Commands.SIGN_FOR(TransactionType)

# Output Vars:
[stats,tx_blob,Account,Fee,Flags,currency,issuer,value,
 Sequence,signer_Account,SigningPubKey,TransactionType,
 hash] = TT_FO.SIGN_FOR(Sign_for_output)  	
```

###### Submit & Sign Details

| *<u>TransactionType</u>*     | *<u>Description</u>*                                         |
| ---------------------------- | :----------------------------------------------------------- |
| **ACCOUNT_SET()**            | An AccountSet transaction modifies the properties of an [account in the XRP Ledger](https://xrpl.org/accountroot.html). |
| **ACCOUNT_DELETE()**         | An AccountDelete transaction deletes an [account](https://xrpl.org/accountroot.html) and any objects it owns in the XRP Ledger, if possible, sending the account's remaining XRP to a specified destination account. See [Deletion of Accounts](https://xrpl.org/accounts.html#deletion-of-accounts) for the requirements to delete an account. |
| **CHECK_CANCEL()**           | Cancels an unredeemed Check, removing it from the ledger without sending any money. The source or the destination of the check can cancel a Check at any time using this transaction type. If the Check has expired, any address can cancel it. |
| **CHECK_CASH()**             | Attempts to redeem a Check object in the ledger to receive up to the amount authorized by the corresponding [CheckCreate transaction](https://xrpl.org/checkcreate.html). Only the `Destination` address of a Check can cash it with a CheckCash transaction. Cashing a check this way is similar to executing a [Payment](https://xrpl.org/payment.html) initiated by the destination.  Since the funds for a check are not guaranteed, redeeming a Check can fail because the sender does not have a high enough balance or because there is not enough liquidity to deliver the funds. If this happens, the Check remains in the ledger and the destination can try to cash it again later, or for a different amount. |
| **CHECK_CREATE()**           | Create a Check object in the ledger, which is a deferred payment that can be cashed by its intended destination. The sender of this transaction is the sender of the Check. |
| **DEPOSIT_PREAUTH()**        | A DepositPreauth transaction gives another account pre-approval to deliver payments to the sender of this transaction. This is only useful if the sender of this transaction is using (or plans to use) [Deposit Authorization](https://xrpl.org/depositauth.html).**You can use this transaction to preauthorize certain counterparties before you enable Deposit Authorization. This may be useful to ensure a smooth transition from not requiring deposit authorization to requiring it.** |
| **ESCROW_CANCEL()**          | Return escrowed XRP to the sender.                           |
| **ESCROW_CREATE()**          | Sequester XRP until the escrow process either finishes or is canceled. |
| **ESCROW_FINNISH()**         | Deliver XRP from a held payment to the recipient.            |
| **OFFER_CANCEL()**           | An OfferCancel transaction removes an Offer object from the XRP Ledger. |
| **OFFER_CREATE()**           | An OfferCreate transaction is effectively a [limit order ](http://en.wikipedia.org/wiki/limit_order). It defines an intent to exchange currencies, and creates an [Offer object](https://xrpl.org/offer.html) if not completely fulfilled when placed. Offers can be partially fulfilled. |
| **PAYMENT()**                | A Payment transaction represents a transfer of value from one account to another. (Depending on the path taken, this can involve additional exchanges of value, which occur atomically.) This transaction type can be used for several [types of payments](https://xrpl.org/payment.html#types-of-payments). **Payments are also the only way to [create accounts](https://xrpl.org/payment.html#creating-accounts).** |
| **PAYMENT_CHANNEL_CLAIM()**  | Claim XRP from a payment channel, adjust the payment channel's expiration, or both. This transaction can be used differently depending on the transaction sender's role in the specified channel:  **More Details: https://xrpl.org/paymentchannelclaim.html** |
| **PAYMENT_CHANNEL_CREATE()** | Create a unidirectional channel and fund it with XRP. The address sending this transaction becomes the "source address" of the payment channel. |
| **PAYMENT_CHANNEL_FUND()**   | Add additional [XRP](https://xrpl.org/xrp.html) to an open [payment channel](https://xrpl.org/payment-channels.html), and optionally update the expiration time of the channel. Only the source address of the channel can use this transaction. |
| **SET_REGULAR_KEY()**        | A `SetRegularKey` transaction assigns, changes, or removes the regular key pair associated with an account. **You can protect your account by assigning a regular key pair to it and using it instead of the master key pair to sign transactions whenever possible. If your regular key pair is compromised, but your master key pair is not, you can use a `SetRegularKey` transaction to regain control of your account.** |
| **SIGNER_LIST_SET()**        | The SignerListSet transaction creates, replaces, or removes a list of signers that can be used to [multi-sign](https://xrpl.org/multi-signing.html) a transaction. This transaction type was introduced by the [MultiSign amendment](https://xrpl.org/known-amendments.html#multisign). |
| **TICKET_CREATE()**          | A TicketCreate transaction sets aside one or more [sequence numbers](https://xrpl.org/basic-data-types.html#account-sequence) as [Tickets](https://xrpl.org/tickets.html). |
| **TRUST_SET()**              | Create or modify a trust line linking two accounts.          |
| **ENABLE_AMENDMENT()**       | An `EnableAmendment` [pseudo-transaction](https://xrpl.org/pseudo-transaction-types.html) marks a change in status of an [amendment](https://xrpl.org/amendments.html) to the XRP Ledger protocol, including: **More Details: https://xrpl.org/enableamendment.html** |
| **SET_FEE()**                | A `SetFee` [pseudo-transaction](https://xrpl.org/pseudo-transaction-types.html) marks a change in [transaction cost](https://xrpl.org/transaction-cost.html) or [reserve requirements](https://xrpl.org/reserves.html) as a result of [Fee Voting](https://xrpl.org/fee-voting.html). **You cannot send a pseudo-transaction, but you may find one when processing ledgers.** |
| **UNL_MODIFY()**             | [Negative UNL](https://xrpl.org/negative-unl.html), indicating that a trusted validator has gone offline or come back online. |
|                              |                                                              |

------



##### LEDGER REQUEST: [NOT TESTED]

```python
from XRP_Node_Commands import XRP_Node_Commands

JSON = XRP_Node_Commands.LEDGER_REQUEST(ledger)
print( JSON)
```

###### **Code Details:**

**Description:** 

- The `ledger_request` command tells server to fetch a specific ledger version from its connected peers. This only works if one of the server's immediately-connected peers has that ledger. You may need to run the command several times to completely fetch a ledger.

**Parameters:** 

- **ledger** [ **int()** ]: *(Optional)* Retrieve the specified ledger by its [Ledger Index](https://xrpl.org/basic-data-types.html#ledger-index).

**Output variables:**

- **JSON**

|      |      |
| ---- | :--- |
|      |      |

##### GATEWAY BALANCE: [NOT TESTED]

```python
from XRP_Node_Commands import XRP_Node_Commands

JSON=XRP_Node_Commands.GATEWAY_BALANCE(account,hotwallet,ledger_index,strict)
print(JSON) # Outputs JSON balance of Gateway
```

###### **Code Details:**

**Description:** 

- The `gateway_balances` command calculates the total balances issued by a given account, optionally excluding amounts held by [operational addresses](https://xrpl.org/issuing-and-operational-addresses.html). 

**Parameters:** 

- **account** ( **str()** ):

     The [Address](https://xrpl.org/basic-data-types.html#addresses) to check. This should be the [issuing address](https://xrpl.org/issuing-and-operational-addresses.html)

- **hotwallet** ( **str()** or **Array** ): 

    *(Optional)* An [operational address](https://xrpl.org/issuing-and-operational-addresses.html) to exclude from the balances issued, or an array of such addresses.

- **ledger_index** ( **str()** ):

     *(Optional)* A 20-byte hex string for the ledger version to use. (See [Specifying Ledgers](https://xrpl.org/basic-data-types.html#specifying-ledgers))

- **strict** ( **Bool** ): 

    *(Optional)* If true, only accept an address or public key for the account parameter. Defaults to false.

**Output variables:**

-  **JSON**

|      |      |
| ---- | :--- |
|      |      |

##### DEPOSIT AUTHORIZED: [NOT TESTED]

```python
from XRP_Node_Commands import XRP_Node_Commands
# Output Variables listed Below in Code Details
[deposit_authorized,
 destination_account,
 ledger_hash,
 ledger_index,
 source_account,
 status,
 validated]=XRP_Node_Commands.DEPOSIT_AUTHORIZED(source_account,
                                                 destination_account,ledger)
print(Output_variables)
```

###### **Code Details:**

**Description:** 

- The `deposit_authorized` command indicates whether one account is authorized to send payments directly to another. See [Deposit Authorization](https://xrpl.org/depositauth.html) for information on how to require authorization to deliver money to your account.

**Parameters:** 

- **source_account** ( **str()** ): 

    The sender of a possible payment.

- **destination_account** ( **str()** ): 

    The recipient of a possible payment.

- **ledger **( **str()** ): 

    *(Optional)* The [ledger index](https://xrpl.org/basic-data-types.html#ledger-index) of the ledger to use, or a shortcut string to choose a ledger automatically. (See [Specifying Ledgers](https://xrpl.org/basic-data-types.html#specifying-ledgers))



**Output variables:** 

- **deposit_authorized,destination_account,ledger_hash,ledger_index,source_account,status,validated**

|      |      |
| ---- | :--- |
|      |      |

##### DOWNLOAD SHARD: [NOT TESTED]

```python
from XRP_Node_Commands import XRP_Node_Commands

message,status = XRP_Node_Commands.DOWNLOAD_SHARD(index,url)
print(message,status)
```

###### **Code Details:**

**Description:** 

- Instructs the server to download a specific [shard of historical ledger data](https://xrpl.org/history-sharding.html) from an external source. Your `rippled` server must be [configured to store history shards](https://xrpl.org/configure-history-sharding.html).

- The external source must provide the shard as an [lz4-compressed ](https://lz4.github.io/lz4/) [tar archive ](https://en.wikipedia.org/wiki/Tar_(computing)) served via HTTPS. The archive must contain the shard directory and data files in NuDB format.
- Downloading and importing shards using this method is usually faster than acquiring the shards individually from the peer-to-peer network. You can also use this method to choose a specific range or set of shards to provide from your server.

**Parameters:** 

- **index** ( **int()** ):

     The index of the shard to retrieve. In the production XRP Ledger, the oldest shard has index 1 and contains ledgers 32750-32768. The next shard has index 2 and contains ledgers 32769-49152, and so on.

- **url** ( **str()** ):

     The URL where this shard can be downloaded. The URL must start with `http://` or `https://` and must end with `.tar.lz4` (not case-sensitive). The web server providing this download must use a valid TLS certificate signed by a trusted Certificate Authority (CA). (`rippled` uses the operating system's CA store.)

**Output variables:**

-  **message,status**

|      |      |
| ---- | :--- |
|      |      |

##### FEATURE: [NOT TESTED]

```python
from XRP_Node_Commands import XRP_Node_Commands

NC = XRP_Node_Commands()
enabled,name,supported,vetoed,status = NC.FEATURE(featureID,variable)

print(enabled,name,supported,vetoed,status)
```

###### **Code Details:**

**Description:** 

- The `feature` command returns information about [amendments](https://xrpl.org/amendments.html) this server knows about, including whether they are enabled and whether the server is voting in favor of those amendments in the [amendment process](https://xrpl.org/amendments.html#amendment-process).

- You can use the `feature` command to configure the server to vote against or in favor of an amendment. This change persists even if you restart the server.

**Parameters:** 

- **featureID** ( **str()** ): 

    (Optional)* The unique ID of an amendment, as hexadecimal; or the short name of the amendment. If provided, limits the response to one amendment. Otherwise, the response lists all amendments.

- **vetoed** ( **Bool** ): 

    (Optional; ignored unless `feature` also specified) If true, instructs the server to vote against the amendment specified by `feature`. If false, instructs the server to vote in favor of the amendment.

**Output variables:** 

- **enabled,name,supported,vetoed,status**

|      |      |
| ---- | :--- |
|      |      |

##### LOG LEVEL: [NOT TESTED]

```python
from XRP_Node_Commands import XRP_Node_Commands

JSON = LOG_LEVEL(partition,severity)
print(JSON)
```

###### **Code Details:**

**Description:** 

- The `log_level` command changes the `rippled` server's logging verbosity, or returns the current logging level for each category (called a *partition*) of log messages.

**Parameters:** 

- **partition** ( **str()** ): 

    *(Optional)* Ignored unless `severity` is provided. Which logging category to modify. If omitted, or if provided with the value `base`, set logging level for all categories.

- **severity** ( **str()** ): 

    *(Optional)* What level of verbosity to set logging at. Valid values are, in order from least to most verbose: `fatal`, `error`, `warn`, `info`, `debug`, and `trace`. If omitted, return current log verbosity for all categories.

**Output variables:**

- **JSON**

|      |      |
| ---- | :--- |
|      |      |

##### PEER RESERVATIONS ADD: [NOT TESTED]

```python
from XRP_Node_Commands import XRP_Node_Commands

node,description,status = XRP_Node_Commands.PEER_RESERVATIONS_DEL(pubkey)
print(node,description,status)
```

###### **Code Details:**

**Description:** 

- The `peer_reservations_add` method adds or updates a reserved slot for a specific peer server in the XRP Ledger [peer-to-peer network](https://xrpl.org/peer-protocol.html).

**Parameters:** 

- **pubkey** ( **str()** ): The [node public key](https://xrpl.org/peer-protocol.html#node-key-pair) of the peer reservation to add a reservation for, in [base58](https://xrpl.org/base58-encodings.html).

**Output variables:** 

- **node,description,status**

|      |      |
| ---- | :--- |
|      |      |

##### PEER RESERVATIONS DEL: [NOT TESTED]

```python
from XRP_Node_Commands import XRP_Node_Commands

node,description,status = XRP_Node_Commands.PEER_RESERVATIONS_DEL(pubkey)
print(node,description,status)
```

###### **Code Details:**

**Description:** 

- The `peer_reservations_del` method removes a specific [peer reservation](https://xrpl.org/peer-protocol.html#fixed-peers-and-peer-reservations), if one exists.

**Parameters:** 

- **pubkey** ( **str()** ): 

    The [node public key](https://xrpl.org/peer-protocol.html#node-key-pair) of the [peer reservation](https://xrpl.org/peer-protocol.html#fixed-peers-and-peer-reservations) to remove, in [base58](https://xrpl.org/base58-encodings.html) format.

**Output variables:** 

- **node,description,status**

|      |      |
| ---- | :--- |
|      |      |

#####  PATH FINDER: [NOT TESTED]

```python
from XRP_Node_Commands import XRP_Node_Commands
from Transaction_Types import Path_finder

#PATH_FINDER_INPUT is needed as input
json_Output = Path_finder.PATH_FINDER_INPUT(source_account,
                                            currencyA,currencyB,
                                            destination_account,
                                            value,issuer)

#Then You can execute Riiple path finder
# Output Variables listed Below in Code Details
[alternatives,
 destination_account,
 destination_amount,
 destination_currencies,
 full_reply,
 source_account,
 source_account,
 status] = XRP_Node_Commands.RIPPLE_PATH_FIND(json_Output)
```

###### **Code Details:** 

**Description:** 

- The `ripple_path_find` method is a simplified version of the [path_find method](https://xrpl.org/path_find.html) that provides a single response with a [payment path](https://xrpl.org/paths.html) you can use right away. It is available in both the WebSocket and JSON-RPC APIs. However, the results tend to become outdated as time passes. Instead of making multiple calls to stay updated, you should instead use the [path_find method](https://xrpl.org/path_find.html) to subscribe to continued updates where possible.

- Although the `rippled` server tries to find the cheapest path or combination of paths for making a payment, it is not guaranteed that the paths returned by this method are, in fact, the best paths.

- Be careful with the pathfinding results from untrusted servers. A server could be modified to return less-than-optimal paths to earn money for its operators. A server may also return poor results when under heavy load. If you do not have your own server that you can trust with pathfinding, you should compare the results of pathfinding from multiple servers run by different parties, to minimize the risk of a single server returning poor results.

**Parameters (PATH_FINDER_INPUT()):** 

- **source_account** ( **str()** ): 

    Unique address of the account that would send funds in a transaction

- **currencyA (from) **& **currencyB (too)**  ( **str()** ): 

    *(Optional)* Array of currencies that the source account might want to spend. Each entry in the array should be a JSON object with a mandatory `currency` field and optional `issuer` field, like how [currency amounts](https://xrpl.org/basic-data-types.html#specifying-currency-amounts) are specified. Cannot contain more than **18** source currencies. By default, uses all source currencies available up to a maximum of **88** different currency/issuer pairs.

- **destination_account** ( **str()** ): 

    Unique address of the account that would receive funds in a transaction

- **value** ( **str()** ):

     [Currency Amount](https://xrpl.org/basic-data-types.html#specifying-currency-amounts) that the destination account would receive in a transaction. **Special case:** [![New in: rippled 0.30.0](https://img.shields.io/badge/New%20in-rippled%200.30.0-blue.svg) ](https://github.com/ripple/rippled/releases/tag/0.30.0) You can specify `"-1"` (for XRP) or provide -1 as the contents of the `value` field (for non-XRP currencies). This requests a path to deliver as much as possible, while spending no more than the amount specified in `send_max` (if provided).

- **issuer** ( **str()** ): Whos is the originall sender

**Output variables:** 

- **alternatives,destination_account,destination_amount,destination_currencies,
                    full_reply,source_account,source_account,status**



|      |      |
| ---- | :--- |
|      |      |

# [ Account_Details ]

##### ACCOUNT CHANNELS [NOT TESTED]

```python
from Account_Details import Account_Details
# Output Variables listed Below in Code Details
[account,channels,
 ledger_index,status,
 validated]=Account_Details.ACCOUNT_CHANNELS(account)
```

###### **Code Details:**

**Description:** 

- The `account_channels` method returns information about an account's Payment Channels. This includes only channels where the specified account is the channel's source, not the destination. (A channel's "source" and "owner" are the same.) All information retrieved is relative to a particular version of the ledger.

**Parameters:** 

- **account** ( **str()** ): 

    The unique identifier of an account, typically the account's [Address](https://xrpl.org/basic-data-types.html#addresses). The request returns channels where this account is the channel's owner/source.

- **destination_account** ( **str()** ): 

    *(Optional)* The unique identifier of an account, typically the account's [Address](https://xrpl.org/basic-data-types.html#addresses). If provided, filter results to payment channels whose destination is this account.

- **ledger** ( **str()** ): 

    *(Optional)* The [ledger index](https://xrpl.org/basic-data-types.html#ledger-index) of the ledger to use, or a shortcut string to choose a ledger automatically. (See [Specifying Ledgers](https://xrpl.org/basic-data-types.html#specifying-ledgers))

**Output variables:** 

- **ledger_hash,ledger_index,status,validated,account,amount,balance,channel_id,destination_account,destination_tag,public_key,public_key_hex,settle_delay,balance**

|      |      |
| ---- | :--- |
|      |      |

##### ACCOUNT CURRENCIES [NOT TESTED]

```python
from Account_Details import Account_Details
# Output Variables listed Below in Code Details
[ledger_index,
 receive_currencies,
 send_currencies,
 status,
 validated] = Account_Details.ACCOUNT_CURRENCIES(account,ledger,strict)
```

###### **Code Details:**

**Description:** 

- The `account_currencies` command retrieves a list of currencies that an account can send or receive, based on its trust lines. (This is not a thoroughly confirmed list, but it can be used to populate user interfaces.)

**Parameters:** 

- **account** ( **str()** ): 

    A unique identifier for the account, most commonly the account's [Address](https://xrpl.org/basic-data-types.html#addresses).

- **ledger** ( **str()** ): 

    *(Optional)* The [ledger index](https://xrpl.org/basic-data-types.html#ledger-index) of the ledger to use, or a shortcut string to choose a ledger automatically. (See [Specifying Ledgers](https://xrpl.org/basic-data-types.html#specifying-ledgers))

- **strict** ( **Bool** ): 

    *(Optional)* If `true`, then the `account` field only accepts a public key or XRP Ledger address. Otherwise, `account` can be a secret or passphrase (not recommended). The default is `false`.

​	**Output variables:** 

- **receive_currencies,send_currencies,status,validated**

|      |      |
| ---- | :--- |
|      |      |

##### ACCOUNT INFO [NOT TESTED]

```python
from Account_Details import Account_Details
# Output Variables listed Below in Code Details
[Account,
 Balance,
 Flags,
 LedgerEntryType,
 OwnerCount,
 PreviousTxnID,
 PreviousTxnLgrSeq,
 Sequence,
 index,
 ledger_index,
 status,
 validated]=Account_Details.ACCOUNT_INFO(account,ledger,strict)
```

###### **Code Details:**

**Description:** 

- The `account_info` command retrieves information about an account, its activity, and its XRP balance. All information retrieved is relative to a particular version of the ledger.

**Parameters:** 

- **account** ( **str()** ): 

    A unique identifier for the account, most commonly the account's [Address](https://xrpl.org/basic-data-types.html#addresses).

- **ledger** ( **str()** ): 

    *(Optional)* The [ledger index](https://xrpl.org/basic-data-types.html#ledger-index) of the ledger to use, or a shortcut string to choose a ledger automatically. (See [Specifying Ledgers](https://xrpl.org/basic-data-types.html#specifying-ledgers))

- **strict** ( **Bool** ):

    *(Optional)* If `true`, then the `account` field only accepts a public key or XRP Ledger address. Otherwise, `account` can be a secret or passphrase (not recommended). The default is `false`.

**Output variables:** 

- **Account,Balance,Flags,LedgerEntryType,OwnerCount,PreviousTxnID,PreviousTxnLgrSeq,Sequence,index,ledger_index,status,validated**

|      |      |
| ---- | :--- |
|      |      |

##### ACCOUNT LINES [NOT TESTED]

```python
from Account_Details import Account_Details
# Output Variables listed Below in Code Details
[account,
 ledger_current_index,
 lines,
 status,
 validated] = Account_Details.ACCOUNT_LINES(account)
```

###### **Code Details:**

**Description:** 

- The `account_lines` method returns information about an account's trust lines, including balances in all non-XRP currencies and assets. All information retrieved is relative to a particular version of the ledger.

**Parameters:** 

- **account** ( **str()** ): A unique identifier for the account, most commonly the account's [Address](https://xrpl.org/basic-data-types.html#addresses).

**Output variables:** 

- **account,ledger_current_index,lines,status,validated**

|      |      |
| ---- | :--- |
|      |      |

##### ACCOUNT OBJECTS [NOT TESTED]

```python
from Account_Details import Account_Details
# Output Variables listed Below in Code Details
[account,
 account_objects,
 ledger_index,
 status,
 validated] = Account_Details.ACCOUNT_OBJECTS(account)
```

###### **Code Details:**

**Description:** 

- The `account_objects` command returns the raw [ledger format](https://xrpl.org/ledger-object-types.html) for all objects owned by an account. For a higher-level view of an account's trust lines and balances, see the [account_lines method](https://xrpl.org/account_lines.html) instead.

The types of objects that may appear in the `account_objects` response for an account include:

- [Offer objects](https://xrpl.org/offer.html) for orders that are currently live, unfunded, or expired but not yet removed. (See [Lifecycle of an Offer](https://xrpl.org/offers.html#lifecycle-of-an-offer) for more information.)
- [RippleState objects](https://xrpl.org/ripplestate.html) for trust lines where this account's side is not in the default state.
- The account's [SignerList](https://xrpl.org/signerlist.html), if the account has [multi-signing](https://xrpl.org/multi-signing.html) enabled.
- [Escrow objects](https://xrpl.org/escrow.html) for held payments that have not yet been executed or canceled.
- [PayChannel objects](https://xrpl.org/paychannel.html) for open payment channels.
- [Check objects](https://xrpl.org/check.html) for pending Checks.
- [DepositPreauth objects](https://xrpl.org/depositpreauth-object.html) for deposit preauthorizations.
- [Ticket objects](https://xrpl.org/known-amendments.html#tickets) for Tickets.

**Parameters:** 

- **account** ( **str()** ): A unique identifier for the account, most commonly the account's address.

**Output variables:**

- **account,account_objects,ledger_index,status,validated**

|      |      |
| ---- | :--- |
|      |      |

##### ACCOUNT OFFERS [NOT TESTED]

```python
from Account_Details import Account_Details
# Output Variables listed Below in Code Details
[account,
 ledger_current_index,
 offers,
 status,
 validated] = Account_Details.ACCOUNT_OFFERS(account,ledger_index,strict)
```

###### **Code Details:**

**Description:**

-  The `account_offers` method retrieves a list of [offers](https://xrpl.org/offers.html) made by a given [account](https://xrpl.org/accounts.html) that are outstanding as of a particular [ledger version](https://xrpl.org/ledgers.html).

**Parameters:** 

- **account** ( **str()** ):

    A unique identifier for the account, most commonly the account's [Address](https://xrpl.org/basic-data-types.html#addresses).

- **ledger_index** ( **str()** ): 

    (Optional, defaults to `current`) The [ledger index](https://xrpl.org/basic-data-types.html#ledger-index) of the ledger to use, or "current", "closed", or "validated" to select a ledger dynamically. (See [Specifying Ledgers](https://xrpl.org/basic-data-types.html#specifying-ledgers))

- **strict** ( **Bool** ): 

    *(Optional)* If `true`, then the `account` field only accepts a public key or XRP Ledger address. Otherwise, `account` can be a secret or passphrase (not recommended). The default is `false`.

**Output variables:** 

- **account,ledger_current_index,offers,status,validated**

|      |      |
| ---- | :--- |
|      |      |

##### ACCOUNT TX [NOT TESTED]

```python
from Account_Details import Account_Details
# Output Variables listed Below in Code Details
[account,
 ledger_index_max,
 ledger_index_min,
 limit,
 status,
 transactions,
 validated] = Account_Details.ACCOUNT_TX(accountID)
```

###### **Code Details:**

**Description:** 

- The `account_tx` method retrieves a list of transactions that involved the specified account.

**Parameters:** 

- **accountID** ( **str()** ): 

    A unique identifier for the account, most commonly the account's address.

​	**Output variables:**

- **account,ledger_index_max,ledger_index_min,limit,status,transactions,validated**

|      |      |
| ---- | :--- |
|      |      |

##### BOOK OFFERS [NOT TESTED]

```python
from Account_Details import Account_Details
# Output Variables listed Below in Code Details
 [ledger_current_index,
  offers,
  status,
  validated] = Account_Details.BOOK_OFFERS(taker_pays,taker_gets)
```

###### **Code Details:**

**Description:** 

- The `book_offers` method retrieves a list of offers, also known as the [order book ](http://www.investopedia.com/terms/o/order-book.asp), between two currencies.

**Parameters:** 

- **taker_pays** ( **str()** ): 

    *(Optional)* The [Address](https://xrpl.org/basic-data-types.html#addresses) of an account to use as a perspective. [Unfunded offers](https://xrpl.org/offers.html#lifecycle-of-an-offer) placed by this account are always included in the response. (You can use this to look up your own orders to cancel them.)

- **taker_gets** ( **str()** ): 

    Specification of which currency the account taking the offer would receive, as an object with `currency` and `issuer` fields (omit issuer for XRP), like [currency amounts](https://xrpl.org/basic-data-types.html#specifying-currency-amounts).

​	**Output variables:**

-  **ledger_current_index,offers,status,validated**

|      |      |
| ---- | :--- |
|      |      |

##### CAN DELETE [NOT TESTED]

```python
from Account_Details import Account_Details
account_data,ledger_index,status = Account_Details.CAN_DELETE(ledger_index)
print(account_data,ledger_index,status)
```

###### **Code Details:**

**Description:**

-  The `can_delete` method informs the `rippled` server of the latest ledger version which may be deleted when using [online deletion with advisory deletion enabled](https://xrpl.org/online-deletion.html#advisory-deletion). If advisory deletion is not enabled, this method does nothing.

**Parameters:** 

- **ledger_index** ( **str()** ): 

    *(Optional)* The [Ledger Index](https://xrpl.org/basic-data-types.html#ledger-index) of the maximum ledger version to allow to be deleted. The special case `never` disables online deletion. The special case `always` enables automatic online deletion as if advisory deletion was disabled. The special case `now` allows online deletion one time at the next validated ledger that meets or exceeds the configured `online_delete` value. If omitted, the server makes no changes (but still replies with the current `can_delete` value).

**Output variables:**

- **account_data,ledger_index,status**

|      |      |
| ---- | :--- |
|      |      |

##### CHANNEL AUTHORIZE [NOT TESTED]

```python
from Account_Details import Account_Details
signature,status=Account_Details.CHANNEL_AUTHORIZE(private_key,
                                                   channel_id,drops)
print(signature,status)
```

###### **Code Details:**

**Description:** 

- The `channel_authorize` method creates a signature that can be used to redeem a specific amount of XRP from a payment channel.

**Parameters:** 

- **private_key** ( **str()** ): 

    *(Optional)* The secret key to use to sign the claim. This must be the same key pair as the public key specified in the channel. Cannot be used with `seed`, `seed_hex`, or `passphrase`.(https://github.com/ripple/rippled/releases/tag/1.4.0)

- **channel_id** ( **str()** ): 

     The unique ID of the payment channel to use.

- **drops** ( **str()** ): Cumulative amount of XRP, in drops, to authorize. If the destination has already received a lesser amount of XRP from this channel, the signature created by this method can be redeemed for the difference.

**Output variables:**

- **signature,status**

|      |      |
| ---- | :--- |
|      |      |

##### CHANNEL VERIFY [NOT TESTED]

```python
from Account_Details import Account_Details
signature_verified,status= Account_Details.CHANNEL_VERIFY(public_key,channel_id,amount,signature)

print(signature_verified,status)
```

###### **Code Details:**

**Description:** 

- The `channel_verify` method checks the validity of a signature that can be used to redeem a specific amount of XRP from a payment channel.

**Parameters:** 

- **public_key** ( **str()** ):

    The public key of the channel and the key pair that was used to create the signature, in hexadecimal or the XRP Ledger's [base58](https://xrpl.org/base58-encodings.html) format.

- **channel_id** ( **str()** ):

    The Channel ID of the channel that provides the XRP. This is a 64-character hexadecimal string.

- **amount** ( **str()** ): 

    The amount of [XRP, in drops](https://xrpl.org/basic-data-types.html#specifying-currency-amounts), the provided `signature` authorizes.

- **signature** ( **str()** ): 

     The signature to verify, in hexadecimal.

**Output variables:**

- **signature_verified,status**

|      |      |
| ---- | :--- |
|      |      |

##### CONNECT [NOT TESTED]

```python
from Account_Details import Account_Details
message,status = Account_Details.CONNECT(ip,port)
print(message,status)
```

###### **Code Details:**

**Description:**

- The `connect` command forces the `rippled` server to connect to a specific peer `rippled` server.

**Parameters:** 

- **ip** ( **str()** ): 

    IP address of the server to connect to

- **port** ( **str()** ): 

    (Optional)* Port number to use when connecting. The default is **2459**

**Output variables**:

- **message,status**



