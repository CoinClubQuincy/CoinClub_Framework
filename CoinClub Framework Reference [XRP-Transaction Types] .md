# **CoinClub Framework Reference     [XRP-Transaction Types]** 

### **All Transaction Types for Submit & Sign**

###### **ACCOUNT_SET**

**Description:** 

- An AccountSet transaction modifies the properties of an [account in the XRP Ledger](https://xrpl.org/accountroot.html).

**Parameters:**

- **Account**  **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

- **Fee** **str()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

- **Sequence** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* The [sequence number](https://xrpl.org/basic-data-types.html#account-sequence) of the account sending the transaction. A transaction is only valid if the `Sequence` number is exactly 1 greater than the previous transaction from the same account. The special case `0` means the transaction is using a [Ticket](https://xrpl.org/tickets.html) instead *(Requires the [TicketBatch amendment](https://xrpl.org/known-amendments.html#ticketbatch) )*.

- **Domain** **int()**

    *(Optional)* The domain that owns this account, as a string of hex representing the ASCII for the domain in lowercase. [Cannot be more than 256 bytes in length. ](https://github.com/ripple/rippled/blob/55dc7a252e08a0b02cd5aa39e9b4777af3eafe77/src/ripple/app/tx/impl/SetAccount.h#L34)

- **SetFlag** **int()**

    *(Optional)* Integer flag to enable for this account.

- **MessageKey** **str()**

    *(Optional)* Public key for sending encrypted messages to this account. To set the key, it must be exactly 33 bytes, with the first byte indicating the key type: `0x02` or `0x03` for secp256k1 keys, `0xED` for Ed25519 keys. To remove the key, use an empty value.

```python
from TransactionType import TransactionType
T = Transaction_Types()

#ACCOUNT_SET
Output = T.ACCOUNT_SET(Account,Fee,Sequence,Domain,SetFlag,MessageKey)

```

------



###### **ACCOUNT_DELETE**

**Description:** 

- An AccountDelete transaction deletes an [account](https://xrpl.org/accountroot.html) and any objects it owns in the XRP Ledger, if possible, sending the account's remaining XRP to a specified destination account. See [Deletion of Accounts](https://xrpl.org/accounts.html#deletion-of-accounts) for the requirements to delete an account.

**Parameters:** 

- **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

- **Destination** **str()**

    The address of an account to receive any leftover XRP after deleting the sending account. Must be a funded account in the ledger, and must not be the sending account.

- **DestinationTag** **int()**

    *(Optional)* Arbitrary [destination tag](https://xrpl.org/source-and-destination-tags.html) that identifies a hosted recipient or other information for the recipient of the deleted account's leftover XRP.

- **Fee** **str()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

- **Sequence** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* The [sequence number](https://xrpl.org/basic-data-types.html#account-sequence) of the account sending the transaction. A transaction is only valid if the `Sequence` number is exactly 1 greater than the previous transaction from the same account. The special case `0` means the transaction is using a [Ticket](https://xrpl.org/tickets.html) instead *(Requires the [TicketBatch amendment](https://xrpl.org/known-amendments.html#ticketbatch) )*.

- **Flags** **int()**

    (Optional)* Set of bit-flags for this transaction.



```python
from TransactionType import TransactionType
T = Transaction_Types()

#ACCOUNT_DELETE
Output = T.ACCOUNT_DELETE(Account,Destination,DestinationTag,Fee,Sequence,Flags)
	
```

------



###### **CHECK_CANCEL**

**Description:** 

- Cancels an unredeemed Check, removing it from the ledger without sending any money. The source or the destination of the check can cancel a Check at any time using this transaction type. If the C heck has expired, any address can cancel it.

**Parameters:**

- **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

- **CheckID** **str()**

     The ID of the [Check ledger object](https://xrpl.org/check.html) to cancel, as a 64-character hexadecimal string.

- **Fee** **str()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

```python
from TransactionType import TransactionType
T = Transaction_Types()

#CHECK_CANCEL
Output = T.CHECK_CANCEL(Account,CheckID,Fee)

```

------



###### **CHECK_CASH**

**Description:**

- Attempts to redeem a Check object in the ledger to receive up to the amount authorized by the corresponding [CheckCreate transaction](https://xrpl.org/checkcreate.html). Only the `Destination` address of a Check can cash it with a CheckCash transaction. Cashing a check this way is similar to executing a [Payment](https://xrpl.org/payment.html) initiated by the destination.

- Since the funds for a check are not guaranteed, redeeming a Check can fail because the sender does not have a high enough balance or because there is not enough liquidity to deliver the funds. If this happens, the Check remains in the ledger and the destination can try to cash it again later, or for a different amount.

**Parameters:**

- **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

- **CheckID** **str()**

     The ID of the [Check ledger object](https://xrpl.org/check.html) to cancel, as a 64-character hexadecimal string.

- **Fee** **str()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

```python
from TransactionType import TransactionType
T = Transaction_Types()

#CHECK_CASH
Output = T.CHECK_CASH(Account,Amount,CheckID,Fee)
	
```

------



###### **CHECK_CREATE**

**Description:** 

- Create a Check object in the ledger, which is a deferred payment that can be cashed by its intended destination. The sender of this transaction is the sender of the Check.

**Parameters:**

- **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

- **Destination** **str()**

    The unique address of the [account](https://xrpl.org/accounts.html) that can cash the Check.

- **SendMax** **str()**

    Maximum amount of source currency the Check is allowed to debit the sender, including [transfer fees](https://xrpl.org/transfer-fees.html) on non-XRP currencies. The Check can only credit the destination with the same currency (from the same issuer, for non-XRP currencies). For non-XRP amounts, the nested field names MUST be lower-case.

- **Expiration** **str()**

    *(Optional)* Time after which the Check is no longer valid, in [seconds since the Ripple Epoch](https://xrpl.org/basic-data-types.html#specifying-time).

- **InvoiceID** **str()**

    *(Optional)* Arbitrary 256-bit hash representing a specific reason or identifier for this Check.

- **DestinationTag** **str()**

    *(Optional)* Arbitrary tag that identifies the reason for the Check, or a hosted recipient to pay.

- **Fee** **str()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

```python
from TransactionType import TransactionType
T = Transaction_Types()

#CHECK_CREATE
Output = T.CHECK_CREATE(Account,Destination,SendMax,Expiration,
								InvoiceID,DestinationTag,Fee)
    
```

------



###### **DEPOSIT_PREAUTH**

**Description:** 

- A DepositPreauth transaction gives another account pre-approval to deliver payments to the sender of this transaction. This is only useful if the sender of this transaction is using (or plans to use) [Deposit Authorization](https://xrpl.org/depositauth.html).
- You can use this transaction to preauthorize certain counterparties before you enable Deposit Authorization. This may be useful to ensure a smooth transition from not requiring deposit authorization to requiring it.

**Parameters:**

- **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

- **Authorize** **str()**

    *(Optional)* The XRP Ledger address of the sender to preauthorize.

- **Fee** **str()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

- **Flags** **int()**

    (Optional)* Set of bit-flags for this transaction.

- **Sequence** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* The [sequence number](https://xrpl.org/basic-data-types.html#account-sequence) of the account sending the transaction. A transaction is only valid if the `Sequence` number is exactly 1 greater than the previous transaction from the same account. The special case `0` means the transaction is using a [Ticket](https://xrpl.org/tickets.html) instead *(Requires the [TicketBatch amendment](https://xrpl.org/known-amendments.html#ticketbatch) )*.

```python
from TransactionType import TransactionType
T = Transaction_Types()

#DEPOSIT_PREAUTH
Output = T.DEPOSIT_PREAUTH(Account,Authorize,Fee,Flags,Sequence)
	
```

------



###### **ESCROW_CANCEL**

**Description:** 

- Return escrowed XRP to the sender.

**Parameters:**

  - **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

  - **Owner** **str()**

    Address of the source account that funded the escrow payment.

  - **OfferSequence**

    Transaction sequence (or [Ticket](https://xrpl.org/tickets.html) number) of [EscrowCreate transaction](https://xrpl.org/escrowcreate.html) that created the escrow to cancel.

```python
from TransactionType import TransactionType
T = Transaction_Types()

#ESCROW_CANCEL
Output = T.ESCROW_CANCEL(Account,Owner,OfferSequence)
	
```

------



###### **ESCROW_CREATE**

**Description:** 

- Sequester XRP until the escrow process either finishes or is canceled.

**Parameters:**

- **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

  - **Amount** **str()**

    Amount of [XRP, in drops](https://xrpl.org/basic-data-types.html#specifying-currency-amounts), to deduct from the sender's balance and escrow. Once escrowed, the XRP can either go to the `Destination` address (after the `FinishAfter` time) or returned to the sender (after the `CancelAfter` time).

  - **Destination** **str()**

    Address to receive escrowed XRP.

  - **CancelAfter** **int()**

    (Optional)* The time, in [seconds since the Ripple Epoch](https://xrpl.org/basic-data-types.html#specifying-time), when this escrow expires. This value is immutable; the funds can only be returned the sender after this time.

  - **FinishAfter** **int()**

    (Optional)* The time, in [seconds since the Ripple Epoch](https://xrpl.org/basic-data-types.html#specifying-time), when the escrowed XRP can be released to the recipient. This value is immutable; the funds cannot move until this time is reached.

  - **Condition** **str()**

    *(Optional)* Hex value representing a [PREIMAGE-SHA-256 crypto-condition ](https://tools.ietf.org/html/draft-thomas-crypto-conditions-02#section-8.1). The funds can only be delivered to the recipient if this condition is fulfilled.

  - **DestinationTag** **int()**

    *(Optional)* Arbitrary tag to further specify the destination for this escrowed payment, such as a hosted recipient at the destination address.

  - **SourceTag** **int()**

    (Optional)* Arbitrary integer used to identify the reason for this payment, or a sender on whose behalf this transaction is made. Conventionally, a refund should specify the initial payment's `SourceTag` as the refund payment's `DestinationTag`.

```python
from TransactionType import TransactionType
T = Transaction_Types()

#ESCROW_CREATE
Output = T.ESCROW_CREATE(Account,Amount,Destination,CancelAfter,
                					FinishAfter,Condition,DestinationTag,SourceTag)
    
```

------



###### **ESCROW_FINNISH**

**Description:** 

- Deliver XRP from a held payment to the recipient.

**Parameters:**

  - **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

  - **Owner** **str()**

    Address of the source account that funded the held payment.

  - **OfferSequence** [Unsigned Integer]

     Transaction sequence of [EscrowCreate transaction](https://xrpl.org/escrowcreate.html) that created the held payment to finish.

  - **Condition** **str()**

    *(Optional)* Hex value matching the previously-supplied [PREIMAGE-SHA-256 crypto-condition ](https://tools.ietf.org/html/draft-thomas-crypto-conditions-02#section-8.1) of the held payment.

  - **Fulfillment** **str()**

    (Optional)* Hex value of the [PREIMAGE-SHA-256 crypto-condition fulfillment ](https://tools.ietf.org/html/draft-thomas-crypto-conditions-02#section-8.1.4) matching the held payment's `Condition`.

```python
from TransactionType import TransactionType
T = Transaction_Types()
  
#ESCROW_FINNISH
Output = T.ESCROW_FINNISH(Account,Owner,OfferSequence,Condition,Fulfillment)

```

------



###### **OFFER_CANCEL**

**Description:** 

- An OfferCancel transaction removes an Offer object from the XRP Ledger.

**Parameters:**

  - **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

  - **Fee** **str()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

  - **Flags** **int()**

    (Optional)* Set of bit-flags for this transaction.

  - **LastLedgerSequence** **int()**

    *Optional; strongly recommended)* Highest ledger index this transaction can appear in. Specifying this field places a strict upper limit on how long the transaction can wait to be validated or rejected. See [Reliable Transaction Submission](https://xrpl.org/reliable-transaction-submission.html) for more details.

  - **OfferSequence** **int()**

    The sequence number (or [Ticket](https://xrpl.org/tickets.html) number) of a previous OfferCreate transaction. If specified, cancel any offer object in the ledger that was created by that transaction. It is not considered an error if the offer specified does not exist.

  - **Sequence** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* The [sequence number](https://xrpl.org/basic-data-types.html#account-sequence) of the account sending the transaction. A transaction is only valid if the `Sequence` number is exactly 1 greater than the previous transaction from the same account. The special case `0` means the transaction is using a [Ticket](https://xrpl.org/tickets.html) instead *(Requires the [TicketBatch amendment](https://xrpl.org/known-amendments.html#ticketbatch) )*.

```python
from TransactionType import TransactionType
T = Transaction_Types()

#OFFER_CANCEL
Output = T.OFFER_CANCEL(Account,Fee,Flags,LastLedgerSequence,
                        OfferSequence,Sequence)
    
```

------



###### **OFFER_CREATE**

**Description:** 

- An OfferCreate transaction is effectively a [limit order ](http://en.wikipedia.org/wiki/limit_order). It defines an intent to exchange currencies, and creates an [Offer object](https://xrpl.org/offer.html) if not completely fulfilled when placed. Offers can be partially fulfilled.

**Parameters:**

  - **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

  - **Fee** **str()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

  - **Flags** **int()**

    (Optional)* Set of bit-flags for this transaction.

  - **LastLedgerSequence** **int()**

    *Optional; strongly recommended)* Highest ledger index this transaction can appear in. Specifying this field places a strict upper limit on how long the transaction can wait to be validated or rejected. See [Reliable Transaction Submission](https://xrpl.org/reliable-transaction-submission.html) for more details.

  - **Sequence** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* The [sequence number](https://xrpl.org/basic-data-types.html#account-sequence) of the account sending the transaction. A transaction is only valid if the `Sequence` number is exactly 1 greater than the previous transaction from the same account. The special case `0` means the transaction is using a [Ticket](https://xrpl.org/tickets.html) instead *(Requires the [TicketBatch amendment](https://xrpl.org/known-amendments.html#ticketbatch) )*.

  - **TakerGets** **int()**

    The amount and type of currency being provided by the offer creator.

  - **currency** **str()**

    The type of currency being requested by the offer creator.

  - **issuer** **str()**

    the one issuing the offer

  - **value** **int()**

    The amount of currency being requested by the offer creator

```python
from TransactionType import TransactionType
T = Transaction_Types()

   
#OFFER_CREATE
Output = T.OFFER_CREATE(Account,Fee,Flags,LastLedgerSequence,Sequence,TakerGets,
               currency,issuer,value)
    
```

------



###### **PAYMENT** [Cold Account only]

**Description:** 

- A Payment transaction represents a transfer of value from one account to another. (Depending on the path taken, this can involve additional exchanges of value, which occur atomically.) This transaction type can be used for several [types of payments](https://xrpl.org/payment.html#types-of-payments).

**Parameters:**

  - **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

  - **Destination** **str()**

    The unique address of the account receiving the payment.

  - **currency**  **str()**

    The type of currency being requested by the offer creator.

  - **value** **int()**

    The amount of currency being requested by the offer creator

  - **issuer** **str()**

    the one issuing the offer

  - **Fee** **str()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

  - **Flags** **int()**

    (Optional)* Set of bit-flags for this transaction.

  - **Sequence** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* The [sequence number](https://xrpl.org/basic-data-types.html#account-sequence) of the account sending the transaction. A transaction is only valid if the `Sequence` number is exactly 1 greater than the previous transaction from the same account. The special case `0` means the transaction is using a [Ticket](https://xrpl.org/tickets.html) instead *(Requires the [TicketBatch amendment](https://xrpl.org/known-amendments.html#ticketbatch) )*.

```python
from TransactionType import TransactionType
T = Transaction_Types()

#PAYMENT
Output = T.PAYMENT(Account,Destination,currency,value,issuer,Fee,Flags,Sequence)
    
```

------



###### **PAYMENT_CHANNEL_CLAIM**

**Description:** 

- Claim XRP from a payment channel, adjust the payment channel's expiration, or both. This transaction can be used differently depending on the transaction sender's role in the specified channel:
- The **source address** of a channel can:
    - Send XRP from the channel to the destination with *or without* a signed Claim.
    - Set the channel to expire as soon as the channel's `SettleDelay` has passed.
    - Clear a pending `Expiration` time.
    - Close a channel immediately, with or without processing a claim first. The source address cannot close the channel immediately if the channel has XRP remaining.
-  The **destination address** of a channel can:
    - Receive XRP from the channel using a signed Claim.
    - Close the channel immediately after processing a Claim, refunding any unclaimed XRP to the channel's source.
- **Any address** sending this transaction can:
    - Cause a channel to be closed if its `Expiration` or `CancelAfter` time is older than the previous ledger's close time. Any validly-formed PaymentChannelClaim transaction has this effect regardless of the contents of the transaction.

**Parameters:**

  - **Channel** **str()**

    The unique ID of the channel, as a 64-character hexadecimal string.

  - **Balance** **str()**

    *(Optional)* Total amount of [XRP, in drops](https://xrpl.org/basic-data-types.html#specifying-currency-amounts), delivered by this channel after processing this claim. Required to deliver XRP. Must be more than the total amount delivered by the channel so far, but not greater than the `Amount` of the signed claim. Must be provided except when closing the channel.

  - **Amount** **str()**

    *(Optional)* The amount of [XRP, in drops](https://xrpl.org/basic-data-types.html#specifying-currency-amounts), authorized by the `Signature`. This must match the amount in the signed message. This is the cumulative amount of XRP that can be dispensed by the channel, including XRP previously redeemed.

  - **Signature** **str()**

    *(Optional)* The signature of this claim, as hexadecimal. The signed message contains the channel ID and the amount of the claim. Required unless the sender of the transaction is the source address of the channel.

  - **PublicKey** **str()**

    (Optional) The public key used for the signature, as hexadecimal. This must match the `PublicKey` stored in the ledger for the channel. Required unless the sender of the transaction is the source address of the channel and the `Signature` field is omitted. (The transaction includes the public key so that `rippled` can check the validity of the signature before trying to apply the transaction to the ledger.)

```python
from TransactionType import TransactionType
T = Transaction_Types()
   
#PAYMENT_CHANNEL_CLAIM
Output=T.PAYMENT_CHANNEL_CLAIM(Channel,Balance,Amount,Signature,PublicKey)   

```

------



###### **PAYMENT_CHANNEL_CREATE**

**Description:** 

- Create a unidirectional channel and fund it with XRP. The address sending this transaction becomes the "source address" of the payment channel.

**Parameters:**

  - **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

  - **Amount** **str()**

    Amount of [XRP, in drops](https://xrpl.org/basic-data-types.html#specifying-currency-amounts), to deduct from the sender's balance and set aside in this channel. While the channel is open, the XRP can only go to the `Destination` address. When the channel closes, any unclaimed XRP is returned to the source address's balance.

  - **Destination** **str()**

    Address to receive XRP claims against this channel. This is also known as the "destination address" for the channel. Cannot be the same as the sender (`Account`).

  - **SettleDelay** **int()**

    Amount of time the source address must wait before closing the channel if it has unclaimed XRP.

  - **PublicKey** **str()**

     The public key of the key pair the source will use to sign claims against this channel, in hexadecimal. This can be any secp256k1 or Ed25519 public key.

  - **CancelAfter** **int()**

    *(Optional)* The time, in [seconds since the Ripple Epoch](https://xrpl.org/basic-data-types.html#specifying-time), when this channel expires. Any transaction that would modify the channel after this time closes the channel without otherwise affecting it. This value is immutable; the channel can be closed earlier than this time but cannot remain open after this time.

  - **DestinationTag** **int()**

    (Optional)* Arbitrary tag to further specify the destination for this payment channel, such as a hosted recipient at the destination address.

  - **SourceTag** **int()**

    (Optional) Arbitrary integer used to identify the reason for this payment, or a sender on whose behalf this transaction is made. Conventionally, a refund should specify the initial payment's `SourceTag` as the refund payment's `DestinationTag`.

```python
from TransactionType import TransactionType
T = Transaction_Types()

#PAYMENT_CHANNEL_CREATE
Output=T.PAYMENT_CHANNEL_CREATE(Account,Amount,Destination,SettleDelay,
                                PublicKey,CancelAfter,
                                DestinationTag,SourceTag)
    
```

------



###### **PAYMENT_CHANNEL_FUND**

**Description:** 

- Add additional [XRP](https://xrpl.org/xrp.html) to an open [payment channel](https://xrpl.org/payment-channels.html), and optionally update the expiration time of the channel. Only the source address of the channel can use this transaction.

**Parameters:**

  - **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

  - **Channel** **str()**

    The unique ID of the channel to fund, as a 64-character hexadecimal string.

  - **Amount** **str()**

    Amount of [XRP, in drops](https://xrpl.org/basic-data-types.html#specifying-currency-amounts), to deduct from the sender's balance and set aside in this channel. While the channel is open, the XRP can only go to the `Destination` address. When the channel closes, any unclaimed XRP is returned to the source address's balance.

  - **Expiration** **int()**

    (Optional)* New `Expiration` time to set for the channel, in [seconds since the Ripple Epoch](https://xrpl.org/basic-data-types.html#specifying-time). This must be later than either the current time plus the `SettleDelay` of the channel, or the existing `Expiration` of the channel. After the `Expiration` time, any transaction that would access the channel closes the channel without taking its normal action. Any unspent XRP is returned to the source address when the channel closes. (`Expiration` is separate from the channel's immutable `CancelAfter` time.) For more information, see the [PayChannel ledger object type](https://xrpl.org/paychannel.html).

```python
from TransactionType import TransactionType
T = Transaction_Types()

#PAYMENT_CHANNEL_FUND
Output = T.PAYMENT_CHANNEL_FUND(Account,Channel,Amount,Expiration)

```

------



###### **SET_REGULAR_KEY**

**Description:** 

- A `SetRegularKey` transaction assigns, changes, or removes the regular key pair associated with an account.
- You can protect your account by assigning a regular key pair to it and using it instead of the master key pair to sign transactions whenever possible. If your regular key pair is compromised, but your master key pair is not, you can use a `SetRegularKey` transaction to regain control of your account.v

**Parameters:**

  - **Flags** **str()**

    (Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

  - **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

  - **Fee** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

  - **RegularKey** **str()**

    (Optional)* A base-58-encoded [Address](https://xrpl.org/basic-data-types.html#addresses) that indicates the regular key pair to be assigned to the account. If omitted, removes any existing regular key pair from the account. Must not match the master key pair for the address.

```python
from TransactionType import TransactionType
T = Transaction_Types()
  
#SET_REGULAR_KEY
Output = T.SET_REGULAR_KEY(Flags,Account,Fee,RegularKey)

```

------



###### **SIGNER_LIST_SET**	**[INCOMPLETE!!!]**

**Description:** This is the description

**Parameters:**

```python
from TransactionType import TransactionType
T = Transaction_Types()

#SIGNER_LIST_SET
Output = T.SIGNER_LIST_SET() 
	
  #Parameters:
    
```

------



###### **TICKET_CREATE**

**Description:** 

- A TicketCreate transaction sets aside one or more [sequence numbers](https://xrpl.org/basic-data-types.html#account-sequence)
- A Ticket in the XRP Ledger is a way of setting aside a [sequence number](https://xrpl.org/basic-data-types.html#account-sequence) for a transaction without sending it right away. Tickets allow transactions to be sent outside of the normal sequence order. One use case for this is to allow for [multi-signed transactions](https://xrpl.org/multi-signing.html) where it may take a while to collect the necessary signatures: while collecting signatures for a transaction that uses a Ticket, you can still send other transactions.

**Parameters:**

  - **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

  - **Fee** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

  - **Sequence** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* The [sequence number](https://xrpl.org/basic-data-types.html#account-sequence) of the account sending the transaction. A transaction is only valid if the `Sequence` number is exactly 1 greater than the previous transaction from the same account. The special case `0` means the transaction is using a [Ticket](https://xrpl.org/tickets.html) instead *(Requires the [TicketBatch amendment](https://xrpl.org/known-amendments.html#ticketbatch) )*.

  - **TicketCount** **int()**

    How many Tickets to create. This must be a positive number and cannot cause the account to own more than 250 Tickets after executing this transaction.

```python
from TransactionType import TransactionType
T = Transaction_Types()

#TICKET_CREATE
Output = T.TICKET_CREATE(Account,Fee,Sequence,TicketCount)

```

------



###### **TRUST_SET**

**Description:** 

- Create or modify a trust line linking two accounts.

**Parameters:**

  - **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

  - **Fee** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

  - **LastLedgerSequence** **int()**

    *Optional; strongly recommended)* Highest ledger index this transaction can appear in. Specifying this field places a strict upper limit on how long the transaction can wait to be validated or rejected. See [Reliable Transaction Submission](https://xrpl.org/reliable-transaction-submission.html) for more details.

  - **currency**  **str()**

    The type of currency being requested by the offer creator.

  - **issuer** **str()**

    the one issuing the offer

  - **value** **int()**

    The amount of currency being requested by the offer creator

  - **Sequence** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* The [sequence number](https://xrpl.org/basic-data-types.html#account-sequence) of the account sending the transaction. A transaction is only valid if the `Sequence` number is exactly 1 greater than the previous transaction from the same account. The special case `0` means the transaction is using a [Ticket](https://xrpl.org/tickets.html) instead *(Requires the [TicketBatch amendment](https://xrpl.org/known-amendments.html#ticketbatch) )*.

```python
from TransactionType import TransactionType
T = Transaction_Types()

#TRUST_SET
Output=T.TRUST_SET(Account,Fee,Flags,LastLedgerSequence,
                   asset,issuer,value,Sequence)
    
```

------



###### **ENABLE_AMENDMENT**

**Description:** 

- An `EnableAmendment` [pseudo-transaction](https://xrpl.org/pseudo-transaction-types.html) marks a change in status of an [amendment](https://xrpl.org/amendments.html) to the XRP Ledger protocol, including:
- A proposed amendment gained supermajority approval from validators.
- A proposed amendment lost supermajority approval.
- A proposed amendment has been enabled.

**Parameters:**

  - **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

  - **Amendment** **str()**

     A unique identifier for the amendment. This is not intended to be a human-readable name. See [Amendments](https://xrpl.org/amendments.html) for a list of known amendments.

  - **Fee** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

  - **LastLedgerSequence** **int()**

    *Optional; strongly recommended)* Highest ledger index this transaction can appear in. Specifying this field places a strict upper limit on how long the transaction can wait to be validated or rejected. See [Reliable Transaction Submission](https://xrpl.org/reliable-transaction-submission.html) for more details.

  - **Sequence** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* The [sequence number](https://xrpl.org/basic-data-types.html#account-sequence) of the account sending the transaction. A transaction is only valid if the `Sequence` number is exactly 1 greater than the previous transaction from the same account. The special case `0` means the transaction is using a [Ticket](https://xrpl.org/tickets.html) instead *(Requires the [TicketBatch amendment](https://xrpl.org/known-amendments.html#ticketbatch) )*.

  - **SigningPubKey** **str()**

    *(Automatically added when signing)* Hex representation of the public key that corresponds to the private key used to sign this transaction. If an empty string, indicates a multi-signature is present in the `Signers` field instead.

```python
from TransactionType import TransactionType
T = Transaction_Types()

   
#ENABLE_AMENDMENT
Output=T.ENABLE_AMENDMENT(Account,Amendment,Fee,LedgerSequence,
                          Sequence,SigningPubKey):
	

```

------



###### **SET_FEE**

**Description:** 

- A `SetFee` [pseudo-transaction](https://xrpl.org/pseudo-transaction-types.html) marks a change in [transaction cost](https://xrpl.org/transaction-cost.html) or [reserve requirements](https://xrpl.org/reserves.html) as a result of [Fee Voting](https://xrpl.org/fee-voting.html).

**Parameters:**  

- **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

  - **BaseFee** **[Unsigned Integer]**

     The charge, in drops of XRP, for the reference transaction, as hex. (This is the [transaction cost](https://xrpl.org/transaction-cost.html) before scaling for load.)

  - **Fee** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

  - **ReferenceFeeUnits** **[Unsigned Integer]**

    The cost, in fee units, of the reference transaction

  - **ReserveBase** **[Unsigned Integer]**

    The base reserve, in drops

  - **ReserveIncrement** **[Unsigned Integer]**

    The incremental reserve, in drops

  - **Sequence** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* The [sequence number](https://xrpl.org/basic-data-types.html#account-sequence) of the account sending the transaction. A transaction is only valid if the `Sequence` number is exactly 1 greater than the previous transaction from the same account. The special case `0` means the transaction is using a [Ticket](https://xrpl.org/tickets.html) instead *(Requires the [TicketBatch amendment](https://xrpl.org/known-amendments.html#ticketbatch) )*.

  - **SigningPubKey** **str()**

    *(Automatically added when signing)* Hex representation of the public key that corresponds to the private key used to sign this transaction. If an empty string, indicates a multi-signature is present in the `Signers` field instead.

  - **date** **[given Date]**

    Date [XX/XX/XXXX]

  - **hash** **[Array of Strings]**

    An array of up to 256 ledger hashes. The contents depend on which sub-type of `LedgerHashes` object this is.

  - **ledger_index** **str()**

    The [ledger index](https://xrpl.org/basic-data-types.html#ledger-index) of the ledger. Some API methods display this as a quoted integer; some display it as a native JSON number.

```python
from TransactionType import TransactionType
T = Transaction_Types()

#SET_FEE
Output = T.SET_FEE(Account,BaseFee,Fee,ReferenceFeeUnits,
                   ReserveBase,ReserveIncrement,Sequence,SigningPubKey,
                   date,hash,ledger_index)
  
```

------



###### **UNL_MODIFY**

**Description:** This is the description

**Parameters:**

  - **Account** **str()**

    *(Required)* The unique address of the [account](https://xrpl.org/accounts.html) that initiated the transaction.

  - **Fee** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* Integer amount of XRP, in drops, to be destroyed as a cost for distributing this transaction to the network. Some transaction types have different minimum requirements. See [Transaction Cost](https://xrpl.org/transaction-cost.html) for details.

  - **LedgerSequence** **int()**

    The [ledger index](https://xrpl.org/basic-data-types.html#ledger-index) where this pseudo-transaction appears. This distinguishes the pseudo-transaction from other occurrences of the same change.

  - **Sequence** **int()**

    *(Required; [auto-fillable](https://xrpl.org/transaction-common-fields.html#auto-fillable-fields))* The [sequence number](https://xrpl.org/basic-data-types.html#account-sequence) of the account sending the transaction. A transaction is only valid if the `Sequence` number is exactly 1 greater than the previous transaction from the same account. The special case `0` means the transaction is using a [Ticket](https://xrpl.org/tickets.html) instead *(Requires the [TicketBatch amendment](https://xrpl.org/known-amendments.html#ticketbatch) )*.

  - **SigningPubKey** **str()**

    *(Automatically added when signing)* Hex representation of the public key that corresponds to the private key used to sign this transaction. If an empty string, indicates a multi-signature is present in the `Signers` field instead.

  - **UNLModifyDisabling** **int()**

     If `1`, this change represents adding a validator to the Negative UNL. If `0`, this change represents removing a validator from the Negative UNL. (No other values are allowed.)

  - **UNLModifyValidator** **str()**

     The validator to add or remove, as identified by its master public key.

```python
from TransactionType import TransactionType
T = Transaction_Types()

#UNL_MODIFY
Output = T.UNL_MODIFY(Account,Fee,LedgerSequence,Sequence,SigningPubKey,
             UNLModifyDisabling,UNLModifyValidator)
  
```





