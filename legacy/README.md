# Legacy: CoinClub Framework 0.0.9 (2021-2022)

> [!CAUTION]
> **Do not use this code.** It is archived for history only and receives no fixes.

Known problems:

- `XRP_Node_Commands.py` and `Account_Details.py` build shell commands from their arguments and run
  them with `shell=True`. Anyone who controls an argument can run commands on the machine.
- Secrets are passed as command-line arguments, which other local users can read in the process list.
- `XLM/Payments.py` contained hardcoded Stellar secrets. They are redacted here but remain in this
  repository's history. On 2026-11-01 the matching accounts existed only on the Stellar testnet, and
  neither had a public-network account.
- Many modules are stubs, or fail on import or at run time.

The final version is tagged `v0.0.9-legacy`. Scraped market data, CocoaPods dependencies, Xcode user
state, compiled Python and a provisioning profile were removed from this tree.

See [`docs/MIGRATION.md`](../docs/MIGRATION.md) for what replaced each module.
