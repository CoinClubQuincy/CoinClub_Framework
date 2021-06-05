

# **CoinClub DashBoard** Framework

## XRP Additional Features

### **Submit Multisigned** 

######  (Admin Dash)

###### - Create Frontend Websocket Apllication for formatting

###### **Code Details:**

**Description:**

-  The `submit_multisigned` command applies a [multi-signed](https://xrpl.org/multi-signing.html) transaction and sends it to the network to be included in future ledgers. (You can also submit multi-signed transactions in binary form using the [`submit` command in submit-only mode](https://xrpl.org/submit.html#submit-only-mode).) This command requires the [MultiSign amendment](https://xrpl.org/known-amendments.html#multisign) to be enabled. This command requires the [MultiSign amendment](https://xrpl.org/known-amendments.html#multisign) to be enabled.
- A successful SignerListSet transaction replaces the account's [`SignerList` object](https://xrpl.org/signerlist.html) in the ledger, or adds one if it did not exist before. An account may not have more than one signer list. To delete a signer list, you must set `SignerQuorum` to `0` *and* omit the `SignerEntries` field. Otherwise, the transaction fails with the error [`temMALFORMED`](https://xrpl.org/tem-codes.html). A transaction to delete a signer list is considered successful even if there was no signer list to delete.
- You cannot create a signer list such that the `SignerQuorum` could never be met. The `SignerQuorum` must be greater than 0 but less than or equal to the sum of the `SignerWeight` values in the list. Otherwise, the transaction fails with the error [`temMALFORMED`](https://xrpl.org/tem-codes.html).
- You can create, update, or remove a signer list using the master key, regular key, or the current signer list, if those methods of signing transactions are available.
- You cannot remove the last method of signing transactions from an account. If an account's master key is disabled (the account has the [`lsfDisableMaster` flag](https://xrpl.org/accountroot.html#accountroot-flags) enabled) and the account does not have a [Regular Key](https://xrpl.org/cryptographic-keys.html) configured, then you cannot delete the signer list from the account. Instead, the transaction fails with the error [`tecNO_ALTERNATIVE_KEY`](https://xrpl.org/tec-codes.html).
- With the [MultiSignReserve amendment](https://xrpl.org/known-amendments.html#multisignreserve) enabled, creating or replacing a signer list enables the `lsfOneOwnerCount` flag on the [SignerList object](https://xrpl.org/signerlist.html). When this flag is enabled, the XRP Ledger is able to lower the [`OwnerCount`](https://xrpl.org/accountroot.html#accountroot-fields) and [owner reserve](https://xrpl.org/reserves.html#owner-reserves) for the signer list. For more information, see [SignerList Flags](https://xrpl.org/signerlist.html#signerlist-flags).

**Parameters:** 

- 

**Output variables:**

- **XXX**



### **[Subscription Methods]**

**Description:**

- The `subscribe` method requests periodic notifications from the server when certain events happen.

- **Types**

    - **Subscribe to Account**

    - **Subscribe to Orderbook** **Streams**

        When you subscribe to one or more order books with the `books` field, you get back any transactions that affect those order books.

    - **Subscribe to Ledger Stream**

        Sends a message whenever the consensus process declares a new validated ledger

    - **Subscribe to Validations Stream**

        The validations stream sends messages whenever it receives validation messages, also called validation votes, regardless of whether or not the validation message is from a trusted validator. The message looks like the following:

    - **Subscribe to Transaction Streams**

        Many subscriptions result in messages about transactions, including the following:

        - The `transactions` stream
        - The `transactions_proposed` stream
        - `accounts` subscriptions
        - `accounts_proposed` subscriptions
        - `book` (Order Book) subscriptions

        The `transactions_proposed` stream, strictly speaking, is a superset of the `transactions` stream: it includes all validated transactions, as well as some suggested transactions that have not yet been included in a validated ledger and may never be. You can identify these "in-flight" transactions by their fields:

        - The `validated` field is missing or has a value of `false`.
        - There is no `meta` or `metadata` field.
        - Instead of `ledger_hash` and `ledger_index` fields specifying in which ledger version the transactions were finalized, there is a `ledger_current_index` field specifying in which ledger version they are currently proposed.

        Otherwise, the messages from the `transactions_proposed` stream are the same as ones from the `transactions` stream.

        Since the only thing that can modify an account or an order book is a transaction, the messages that are sent as a result of subscribing to particular `accounts` or `books` also take the form of transaction messages, the same as the ones in the `transactions` stream. The only difference is that you only receive messages for transactions that affect the accounts or order books you're watching.

        The `accounts_proposed` subscription works the same way, except it also includes unconfirmed transactions, like the `transactions_proposed` stream, for the accounts you're watching.

    - **Subscribe to Peer Status Stream**

        The admin-only `peer_status` stream reports a large amount of information on the activities of other `rippled` servers to which this server is connected, in particular their status in the consensus process.

        Peer Status stream messages represent some event where the status of the peer `rippled` server changed. These messages are JSON objects with the following fields:

    - **Subscribe to Consensus Stream**

        The `consensus` stream sends `consensusPhase` messages when [the consensus process](https://xrpl.org/consensus.html) changes phase. The message contains the new phase of consensus the server is in.