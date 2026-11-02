# Migrating from 0.0.9

Version 1.0 replaces the old framework. It uses each chain's official SDK instead of shelling out to
a local `rippled`, so it no longer needs a node installed.

## XRP Ledger

| 0.0.9 | 1.0 |
|---|---|
| `XRP_Node_Commands.WALLET_GENERATOR_MANUAL(passphrase)` | `chain.create_wallet()` |
| `XRP_Node_Commands.SIGN`, `SUBMIT` | `chain.submit(wallet, "Payment", ...)` |
| `XRP_Node_Commands.SIGN_FOR`, `SUBMIT_MULTISIGNED` | `chain.prepare_multisigned`, `chain.sign_for`, `chain.submit_multisigned` |
| `Account_Details.ACCOUNT_INFO(account)` and the rest of that class | `chain.account_info(account=account)` and matching lowercase names |
| `XRP_Node_Commands.LEDGER_REQUEST`, `GATEWAY_BALANCE`, `DEPOSIT_AUTHORIZED`, `FEATURE`, `RIPPLE_PATH_FIND` | `chain.ledger`, `chain.gateway_balances`, `chain.deposit_authorized`, `chain.feature`, `chain.ripple_path_find` |
| `VALIDATION_CREATE_MANUAL`, `CAN_DELETE`, `CONNECT`, `LOG_LEVEL`, `DOWNLOAD_SHARD`, `PEER_RESERVATIONS_ADD`, `PEER_RESERVATIONS_DEL`, `COMAND_CONTROL` | `chain.rpc("validation_create", ...)` and so on, against your own node with `connect("xrpl", url=...)`. These are admin methods, so public servers refuse them |
| `Transaction_Types.PAYMENT(...)` | `chain.transfer(...)` or `chain.submit(wallet, "Payment", ...)` |
| `Transaction_Types.ACCOUNT_SET`, `CHECK_CREATE`, `ESCROW_CREATE`, `OFFER_CREATE`, `TRUST_SET` and the other user transactions | `chain.submit(wallet, "AccountSet", ...)` with the xrpl-py type name. Note that `ESCROW_FINNISH` is now `EscrowFinish` |
| `Transaction_Types.ENABLE_AMENDMENT`, `SET_FEE`, `UNL_MODIFY` | Removed. Only validators can apply these pseudo-transactions, so they cannot be submitted |
| `XRP_API_v2` | Removed. Ripple's Data API v2 is deprecated, as the old code noted |
| `XUMM.Functions`, `XUMM.Basic_API` | `coinclub.xaman.XamanClient`. Requests now carry API credentials, which the old code never sent |

## Stellar

| 0.0.9 | 1.0 |
|---|---|
| `XLM_Wallet.KEYPAIR_GENERATE` | `chain.create_wallet()` |
| `XLM_Wallet.CREATE_ACCOUNT` | `chain.request_test_funds(wallet)` or `chain.create_account(...)` |
| `Payments.PAY` | `chain.transfer(...)` |
| `Operation`, `Call_Builder`, `API_XLM`, `Memo`, `Client` | Use `chain.submit(wallet, [operation])` with stellar-sdk operations, and `chain.server` for Horizon queries |

## Other modules

| 0.0.9 | 1.0 |
|---|---|
| `Basic_Liquidity_Algorithm.Strategies.Liquid_Mean`, `Liquid_Top`, `Liquid_Bottom` | `coinclub.liquidity.mean`, `top`, `bottom` |
| `Liquid_Stable_Narrow`, `Liquid_Stable_Wide` | `liquidity.stable` with a small or large `width` |
| `DayRangeLiquidity`, `WeekRangeLiquidity`, `MonthRangeLiquidity` | `liquidity.from_range` with that period's low and high |
| `Exchange_Liberary.Bitrue_API` | `coinclub.exchange.BitrueClient` |
| `Live_Gateway` | `coinclub.gateway.PaymentGateway` |
| `Cloud/AWS.py` | `coinclub.aws` and `coinclub.api` |
| `FLRcc.py` | `connect("flare")` |

## Not carried forward

These stay in `legacy/` for reference, because they are not part of a Python library:

- `WallApp_IOS`, the card and case app
- `DAML_Apps` and the Corda notes
- `Cloud/GCloud.py`, `Cloud/Traditional_DBs` and `File_Manager`, which were stubs or general utilities
- The empty `App_Node` and `Execute_Node`

Not built: EOS signing, Filecoin native `f1` and `f3` addresses, and placing orders on centralized
exchanges.
