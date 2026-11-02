# Security

Please report vulnerabilities privately through
[GitHub security advisories](https://github.com/CoinClubQuincy/CoinClub_Framework/security/advisories/new),
not in a public issue.

## What the library does

- Generates and signs on your machine. Secrets are never sent to a node or API.
- Refuses mainnet writes unless you pass `allow_mainnet=True`.
- Refuses floats as amounts.
- On EVM chains, checks the node's chain ID before signing.
- On the XRP Ledger, counts delivered amounts rather than requested amounts.

## What it does not do

- Protect a secret in memory, or secure the machine it runs on.
- Stop a transaction once your code has asked for it.
- Verify anything your node tells you. A malicious node can report false balances and payments, so
  run your own or use one you trust before relying on the gateway for large amounts.

It has had no independent security audit.
