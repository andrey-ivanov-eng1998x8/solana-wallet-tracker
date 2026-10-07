# solana-wallet-tracker

Small CLI that polls the Solana JSON-RPC for recent token transfers on a fixed list of wallets. I run it from cron to get a quick digest without dealing with websockets or paid APIs.

It hits `getSignaturesForAddress` and `getParsedTransaction`, filters for SPL token activity, and prints a plain text summary. Nothing fancy.

## Install

```
pip install httpx
```

Or just use your system packages if you already have `httpx`.

## Run

With no args it shows a demo against embedded fixture data:

```
python soltracker.py
```

Watch live wallets:

```
python soltracker.py --rpc https://api.mainnet-beta.solana.com --wallets wallet1,wallet2 --hours 24
```

## Notes

- Public RPC rate limits are aggressive; I added a small sleep between requests.
- Token mints are looked up via a tiny hardcoded cache of common ones (USDC, USDT, SOL wrapped, etc). Unknown mints print raw.
- I keep my real wallet list in a shell wrapper, not in here.

<!-- verified: 2026-10-07 -->
