import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

try:
    import httpx
except ImportError as _exc:
    sys.exit(f"missing dependency '{_exc.name}'. run: pip install -r requirements.txt")

SOLANA_RPC = "https://api.mainnet-beta.solana.com"
LAMPORTS_PER_SOL = 1_000_000_000

FIXTURE_TRANSFERS = [
    {
        "signature": "4nTqC8m8ZzFqYmN2N7kPQrHtY7W3p9vLkR5sT6uVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890abcd",
        "timestamp": "2024-01-15T09:23:17+00:00",
        "from": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "to": "3pKNy2jYg7r8QZ9mNpLkRt5sTuVwXyZaBcDeFgHiJkLm",
        "amount_lamports": 500000000000,
        "token": "SOL",
        "success": True,
    },
    {
        "signature": "5oUrD9n9AaRbNcOpQ1rStUvWxYzAbCdEfGhIjKlMnOpQrStUvWxYz2345678901efgh",
        "timestamp": "2024-01-15T08:45:33+00:00",
        "from": "3pKNy2jYg7r8QZ9mNpLkRt5sTuVwXyZaBcDeFgHiJkLm",
        "to": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "amount_lamports": 12500000000,
        "token": "USDC",
        "success": True,
    },
    {
        "signature": "6pVsE0o0BcSdTfGhIjKlMnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWxYz3456789012ghij",
        "timestamp": "2024-01-14T23:17:02+00:00",
        "from": "9qLMn3kZh8s9ARoNpQrTu6uVxYzAbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIjKl",
        "to": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "amount_lamports": 7500000000000,
        "token": "SOL",
        "success": True,
    },
    {
        "signature": "7qWtF1p1CdTeUhJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZ",
        "timestamp": "2024-01-14T18:52:41+00:00",
        "from": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "to": "2mJHx4fUv5w6XyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZ",
        "amount_lamports": 25000000000,
        "token": "BONK",
        "success": False,
    },
    {
        "signature": "8rXuG2q2DfUhVkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaB",
        "timestamp": "2024-01-14T14:08:19+00:00",
        "from": "5tFGp6iRw8u9CVqNoPsTu3vWxYzAbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIjKlMnOp",
        "to": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "amount_lamports": 100000000000,
        "token": "SOL",
        "success": True,
    },
    {
        "signature": "9sYvH3r3EgWiXmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcD",
        "timestamp": "2024-01-14T06:33:55+00:00",
        "from": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "to": "8uQRs7kTw9y0DWxYzAbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWxYz",
        "amount_lamports": 420000000000,
        "token": "RAY",
        "success": True,
    },
    {
        "signature": "aTwZI4s4FhXjNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFg",
        "timestamp": "2024-01-13T21:47:28+00:00",
        "from": "4rHNo8jUv1w2XyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBc",
        "to": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "amount_lamports": 5000000000,
        "token": "USDT",
        "success": True,
    },
    {
        "signature": "bUxAJ5t5GiYkNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgH",
        "timestamp": "2024-01-13T15:12:07+00:00",
        "from": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "to": "6vSTu9lWx3y4YZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcD",
        "amount_lamports": 89000000000,
        "token": "SOL",
        "success": True,
    },
    {
        "signature": "cVyBK6u6HjZlNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHi",
        "timestamp": "2024-01-13T03:58:44+00:00",
        "from": "1aBCd3eFg5hIjKlMnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIjKlMnOpQ",
        "to": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "amount_lamports": 1500000000000,
        "token": "SOL",
        "success": True,
    },
    {
        "signature": "dWzCL7v7IkAmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJ",
        "timestamp": "2024-01-12T19:25:11+00:00",
        "from": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "to": "0xAbCdEf1234567890aBcDeF1234567890AbCdEf12",
        "amount_lamports": 33000000000,
        "token": "JUP",
        "success": True,
    },
    {
        "signature": "eXaDM8w8JlBnNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJk",
        "timestamp": "2024-01-12T11:07:59+00:00",
        "from": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "to": "3pKNy2jYg7r8QZ9mNpLkRt5sTuVwXyZaBcDeFgHiJkLm",
        "amount_lamports": 67000000000,
        "token": "SOL",
        "success": True,
    },
    {
        "signature": "fYbEN9x9KmCoNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkL",
        "timestamp": "2024-01-12T04:41:36+00:00",
        "from": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "to": "9qLMn3kZh8s9ARoNpQrTu6uVxYzAbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIjKl",
        "amount_lamports": 21000000000,
        "token": "MNGO",
        "success": False,
    },
    {
        "signature": "gZcFO0y0LnDpNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLm",
        "timestamp": "2024-01-11T22:14:13+00:00",
        "from": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "to": "5tFGp6iRw8u9CVqNoPsTu3vWxYzAbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIjKlMnOp",
        "amount_lamports": 445000000000,
        "token": "USDC",
        "success": True,
    },
    {
        "signature": "hAdGP1z1MoEqNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmN",
        "timestamp": "2024-01-11T16:38:50+00:00",
        "from": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "to": "2mJHx4fUv5w6XyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZ",
        "amount_lamports": 78000000000,
        "token": "SOL",
        "success": True,
    },
    {
        "signature": "iBeHQ2a2NpFrNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNo",
        "timestamp": "2024-01-11T09:52:27+00:00",
        "from": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "to": "4rHNo8jUv1w2XyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBc",
        "amount_lamports": 156000000000,
        "token": "BONK",
        "success": True,
    },
    {
        "signature": "jCfIR3b3OqGsNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoP",
        "timestamp": "2024-01-10T23:15:04+00:00",
        "from": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "to": "8uQRs7kTw9y0DWxYzAbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWxYz",
        "amount_lamports": 92000000000,
        "token": "RAY",
        "success": True,
    },
    {
        "signature": "kDgJS4c4PrHtNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPq",
        "timestamp": "2024-01-10T14:47:41+00:00",
        "from": "6vSTu9lWx3y4YZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcD",
        "to": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "amount_lamports": 2300000000000,
        "token": "SOL",
        "success": True,
    },
    {
        "signature": "lEhKT5d5QsIuNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqR",
        "timestamp": "2024-01-10T07:21:18+00:00",
        "from": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "to": "1aBCd3eFg5hIjKlMnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIjKlMnOpQ",
        "amount_lamports": 54000000000,
        "token": "JUP",
        "success": True,
    },
    {
        "signature": "mFiLU6e6RtJvNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRs",
        "timestamp": "2024-01-09T20:54:55+00:00",
        "from": "0xAbCdEf1234567890aBcDeF1234567890AbCdEf12",
        "to": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "amount_lamports": 112000000000,
        "token": "USDC",
        "success": True,
    },
    {
        "signature": "nGjMV7f7SuKwNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsT",
        "timestamp": "2024-01-09T13:28:32+00:00",
        "from": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "to": "3pKNy2jYg7r8QZ9mNpLkRt5sTuVwXyZaBcDeFgHiJkLm",
        "amount_lamports": 89000000000,
        "token": "SOL",
        "success": True,
    },
]

WALLETS = [
    "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    "3pKNy2jYg7r8QZ9mNpLkRt5sTuVwXyZaBcDeFgHiJkLm",
    "9qLMn3kZh8s9ARoNpQrTu6uVxYzAbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIjKl",
]


@dataclass
class Transfer:
    signature: str
    timestamp: datetime
    from_addr: str
    to_addr: str
    amount_sol: float
    token: str
    success: bool
    wallet: str


def parse_fixture(data: list[dict]) -> list[Transfer]:
    out = []
    for item in data:
        wallet = item["from"] if item["from"] in WALLETS else item["to"]
        out.append(Transfer(
            signature=item["signature"],
            timestamp=datetime.fromisoformat(item["timestamp"]),
            from_addr=item["from"],
            to_addr=item["to"],
            amount_sol=item["amount_lamports"] / LAMPORTS_PER_SOL,
            token=item["token"],
            success=item["success"],
            wallet=wallet,
        ))
    return out


def fetch_signature(client: httpx.Client, wallet: str, limit: int = 20) -> list[dict]:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [wallet, {"limit": limit}],
    }
    resp = client.post(SOLANA_RPC, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"RPC error: {data['error']}")
    return data.get("result", [])


def fetch_transaction(client: httpx.Client, signature: str) -> dict:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "json", "maxSupportedTransactionVersion": 0}],
    }
    resp = client.post(SOLANA_RPC, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"RPC error: {data['error']}")
    return data.get("result", {})


def _find_wallet_token_delta(wallet: str, pre_token: list, post_token: list) -> Optional[tuple[float, str]]:
    # map mint to balance changes for our wallet
    mint_deltas: dict[str, float] = {}
    for entry in pre_token:
        if entry.get("owner") != wallet:
            continue
        mint = entry.get("mint", "UNKNOWN")
        ui = float(entry.get("uiTokenAmount", {}).get("amount", 0))
        mint_deltas[mint] = mint_deltas.get(mint, 0) - ui
    for entry in post_token:
        if entry.get("owner") != wallet:
            continue
        mint = entry.get("mint", "UNKNOWN")
        ui = float(entry.get("uiTokenAmount", {}).get("amount", 0))
        mint_deltas[mint] = mint_deltas.get(mint, 0) + ui
    if not mint_deltas:
        return None
    # pick the largest delta
    mint, delta = max(mint_deltas.items(), key=lambda x: abs(x[1]))
    if abs(delta) < 1e-9:
        return None
    return delta, mint


def extract_transfer(wallet: str, signature: str, tx_data: dict) -> Optional[Transfer]:
    meta = tx_data.get("meta", {})
    success = meta.get("err") is None

    tx = tx_data.get("transaction", {})
    message = tx.get("message", {})
    account_keys = message.get("accountKeys", [])

    pre_balances = meta.get("preBalances", [])
    post_balances = meta.get("postBalances", [])

    if not account_keys or len(pre_balances) != len(post_balances):
        return None

    try:
        wallet_idx = account_keys.index(wallet)
    except ValueError:
        return None

    delta = post_balances[wallet_idx] - pre_balances[wallet_idx]
    token = "SOL"

    if delta == 0:
        pre_token = meta.get("preTokenBalances", [])
        post_token = meta.get("postTokenBalances", [])
        token_result = _find_wallet_token_delta(wallet, pre_token, post_token)
        if token_result is None:
            return None
        delta, token = token_result

    other_idx = 1 - wallet_idx if len(account_keys) == 2 else 0
    other_addr = account_keys[other_idx] if other_idx != wallet_idx else account_keys[0]

    block_time = tx_data.get("blockTime")
    if block_time:
        ts = datetime.fromtimestamp(block_time, tz=timezone.utc)
    else:
        ts = datetime.now(timezone.utc)

    return Transfer(
        signature=signature,
        timestamp=ts,
        from_addr=wallet if delta < 0 else other_addr,
        to_addr=wallet if delta > 0 else other_addr,
        amount_sol=abs(delta) / LAMPORTS_PER_SOL if token == "SOL" else abs(delta),
        token=token,
        success=success,
        wallet=wallet,
    )


def poll_wallets(wallets: list[str], limit: int = 20) -> list[Transfer]:
    transfers = []
    with httpx.Client() as client:
        for wallet in wallets:
            try:
                sigs = fetch_signature(client, wallet, limit)
            except Exception as exc:
                print(f"couldn't fetch signatures for {wallet[:8]}...: {exc}", file=sys.stderr)
                continue
            for sig_info in sigs:
                sig = sig_info.get("signature")
                if not sig:
                    continue
                try:
                    tx = fetch_transaction(client, sig)
                    if not tx:
                        continue
                    t = extract_transfer(wallet, sig, tx)
                    if t:
                        transfers.append(t)
                except Exception as exc:
                    print(f"failed tx {sig[:16]}...: {exc}", file=sys.stderr)
                    continue
    return transfers


def format_summary(transfers: list[Transfer]) -> None:
    if not transfers:
        print("no transfers found")
        return

    by_token: dict[str, list[Transfer]] = {}
    for t in transfers:
        by_token.setdefault(t.token, []).append(t)

    total_volume = sum(t.amount_sol for t in transfers)
    successful = [t for t in transfers if t.success]
    failed = [t for t in transfers if not t.success]

    print(f"scanned {len(transfers)} recent transfers across {len(set(t.wallet for t in transfers))} wallets")
    print(f"total volume: {total_volume:,.4f} SOL-equivalent")
    print(f"successful: {len(successful)}  failed: {len(failed)}")
    print()

    print("breakdown by token:")
    for token, txs in sorted(by_token.items(), key=lambda x: -sum(t.amount_sol for t in x[1])):
        vol = sum(t.amount_sol for t in txs)
        print(f"  {token:6s}  {len(txs):3d} tx  {vol:>12,.4f}  ({100*vol/total_volume:5.1f}%)")

    print()
    print("latest 5 transfers:")
    for t in sorted(transfers, key=lambda x: x.timestamp, reverse=True)[:5]:
        arrow = "->" if t.from_addr in WALLETS else "<-"
        short_sig = t.signature[:16] + "..."
        print(f"  {t.timestamp.strftime('%Y-%m-%d %H:%M')}  {arrow}  {t.amount_sol:>10.4f} {t.token:5s}  {short_sig}")


def run_cached_scan() -> int:
    transfers = parse_fixture(FIXTURE_TRANSFERS)
    format_summary(transfers)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="watch solana wallets for recent transfers",
        usage="python soltracker.py [--wallets ADDR [ADDR ...]] [--limit N]",
    )
    parser.add_argument("--wallets", nargs="+", default=[], help="wallet addresses to watch")
    parser.add_argument("--limit", type=int, default=20, help="max signatures per wallet")
    parser.add_argument("--rpc", default=SOLANA_RPC, help="solana rpc endpoint")
    args = parser.parse_args()

    if not args.wallets:
        return run_cached_scan()

    wallets = args.wallets
    transfers = poll_wallets(wallets, args.limit)
    format_summary(transfers)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main() or 0)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as _exc:
        if os.environ.get("DEBUG"):
            raise
        _prog = os.path.basename(sys.argv[0])
        sys.exit(f"{_prog}: {type(_exc).__name__}: {_exc}")
