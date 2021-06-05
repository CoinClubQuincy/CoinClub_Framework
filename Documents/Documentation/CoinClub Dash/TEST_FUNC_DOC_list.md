# **CoinClub Function Test Document** Version 0.8.6

### **XRP Node Function Liberary**

- 73 XRP_Node Functions
- 26 XUMM Functions
- 8 XRP Commands Not Listed Yet
    - Will be in version 2.0.1

**Notes:**

- Ready for build and Test

#### **XRP_Node_Commands**

- WALLET_GENERATOR_MANUAL(passphrase)**[✓]**
- VALIDATION_CREATE_MANUAL(passphrase)**[✓]**
- COMAND_CONTROL(CLI_command) **[✓]**

    - onsensus_info **[✓]**
- get_counts **[✓]**
    - ledger_accept **[stand alone mode]**
- ledger_cleaner **[✓]**
    - ledger_closed **[✓]**
- ledger_current **[✓]**
    - logrotate  **[✓]**
- peers **[✓]**
    - ping **[✓]**
- random **[✓]**
    - peer_reservations_list **[✓]**
- server_info **[✓]**
    - server_state  **[✓]**
- stop  **[✓]**
    - validation_create **[✓]**
- validator_list_sites **[✓]**
    - version **[✓]**
- wallet_propose **[✓]** 

### **(Basics)**

-  **(Complete LAST)**  SUBMIT(Type,TransactionType)

- **(Complete LAST)** SIGN(TransactionType)

    

    ### **(Advance)**

-  **(Complete LAST)** SUBMIT_MULTISIGNED(TransactionType)

- **(Complete LAST)** SIGN_FOR(TransactionType)

    

    - #### **TransactionTypes**

        - ACCOUNT_SET()

        - ACCOUNT_DELETE()

        - CHECK_CANCEL()

        - CHECK_CASH()

        - CHECK_CREATE()

        - DEPOSIT_PREAUTH()

        - ESCROW_CANCEL()

        - ESCROW_CREATE()

        - ESCROW_FINNISH()

        - OFFER_CANCEL()

        - OFFER_CREATE()

        - PAYMENT()

        - PAYMENT_CHANNEL_CLAIM()

        - PAYMENT_CHANNEL_CREATE()

        - PAYMENT_CHANNEL_FUND()

        - SET_REGULAR_KEY()

        - SIGNER_LIST_SET()**(Incomplete)**

        - DEFAULT_SUBMIT_MULTISIGNED()

        - TICKET_CREATE()

        - TRUST_SET()

        - ENABLE_AMENDMENT()

        - SET_FEE()

        - UNL_MODIFY

            

            - **Test Transaction_Types_Format_Output**

                - SIGN(Comand_Output)

                - SIGN_FOR(Comand_Output)

                - SUBMIT(Comand_Output)

                - DEFAULT_SUBMIT_MULTISIGNED() **(Incomplete)**

                    

- LEDGER_REQUEST(ledger)  **[✓]**

- GATEWAY_BALANCES(account,hotwallet)**[✓]**

- DEPOSIT_AUTHORIZED(source_account,destination_account) **[✓]**

    


#### **Account_Details**

- ACCOUNT_CHANNELS(account) **[✓]**
- ACCOUNT_CURRENCIES(account) **[✓]**
- ACCOUNT_INFO(account) **[✓]**
- ACCOUNT_LINES(account)  **[✓]**
- ACCOUNT_OBJECTS(account)  **[✓]**
- ACCOUNT_OFFERS(account) **[✓]**
- ACCOUNT_TX(accountID) **[✓]**
- BOOK_OFFERS(taker_pays,taker_gets) **[✓]**

    

      

### **MIS**

- FEATURE(featureID) **[✓]**

- LOG_LEVEL(severity) **[✓]**

- PEER_RESERVATIONS_ADD(pubkey,description) **[✓]**

- PEER_RESERVATIONS_DEL(pubkey) **[✓]**

- RIPPLE_PATH_FIND(json) 

    - **Test PATH_FINDER_INPUT()**

### **MANUAL** for right now

- CAN_DELETE(ledger_index)
- DOWNLOAD_SHARD(index,url)
- CONNECT(ip,port)
- CHANNEL_AUTHORIZE(private_key,channel_id,drops)
- CHANNEL_VERIFY(public_key,channel_id,amount,signature)

#### **XUMM**

- GET_API(api_var)
    - payload_uuid
        - **Test VAR_OUTPUTS**
    - custom_identifier
        - **Test VAR_OUTPUTS**
    - payload_uuid
        - **Test VAR_OUTPUTS**
    - token
        - **Test VAR_OUTPUTS**
    - ping
        - **Test VAR_OUTPUTS**
    - curated-assets
        - **Test VAR_OUTPUTS**
    - txid
        - **Test VAR_OUTPUTS**
    - kyc-status
        - **Test VAR_OUTPUTS**
    - payload
        - **Test VAR_OUTPUTS**
- KYC_STATUS()
    - **Test VAR_OUTPUTS**
- PAYLOAD(txblob,submit,multisign,expire)
    - **Test VAR_OUTPUTS **
- EVENT(user_token,subtitle,body,tx,account)
    - **Test VAR_OUTPUTS **
- PUSH(user_token,subtitle,body,JSON_data)
    - **Test VAR_OUTPUTS **



#### **----- Commands Not Listed ----- **

- subscribe [Webhook needed]
- unsubscribe [Webhook needed]
- noripple_check [Webhook needed]
- ledger_entry [Webhook needed]
- ledger_data [Webhook needed]
- path_find [Webhook needed]
- fee [Webhook needed]
- manifest [Webhook needed]

