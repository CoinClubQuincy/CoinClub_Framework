# Changelog

## 1.0.0 (unreleased)

Complete rewrite as an installable package, and not compatible with 0.0.9.

- One `Chain` interface across XRP Ledger, Stellar, XDC, Flare, Filecoin (FEVM), Ethereum, Algorand,
  Cardano and read-only EOS, built on each chain's official SDK
- Mainnet writes need `allow_mainnet=True`, and amounts reject floats
- Liquidity ladders and DEX offers on the XRP Ledger and Stellar
- Non-custodial payment gateway, with DynamoDB storage
- Xaman platform client, Bitrue market data and a command line
- Read-only, metered AWS Lambda API

The old code moved to `legacy/`. It shelled out to `rippled` with `shell=True`, so do not use it.
