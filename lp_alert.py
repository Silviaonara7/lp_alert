#!/usr/bin/env python3
"""
LPAlert — мониторинг крупных операций Mint/Burn в пуле UniswapV2/SushiSwap.

При обнаружении Mint с amount0 >= MIN_LIQ0_THRESHOLD выводит оповещение.
Всех Burn тоже логируем для полноты картины.
"""

import os
import time
from decimal import Decimal

from web3 import Web3

# --- Чтение настроек из окружения ---
RPC_WS_URL          = os.getenv("ETH_WS_URL")  # WebSocket RPC, нужен для фильтров
POOL_ADDRESSES      = os.getenv("POOL_ADDRESSES", "").split(",")
MIN_LIQ0_THRESHOLD  = Decimal(os.getenv("MIN_LIQ0_THRESHOLD", "1000000000000000000"))  # 1 token0 в wei
POLL_INTERVAL       = int(os.getenv("POLL_INTERVAL", "5"))  # сек

if not RPC_WS_URL or not POOL_ADDRESSES or POOL_ADDRESSES == [""]:
    print("❗ Задайте ETH_WS_URL и POOL_ADDRESSES (comma‑sep).")
    exit(1)

w3 = Web3(Web3.WebsocketProvider(RPC_WS_URL))
if not w3.is_connected():
    print("❗ Не удалось подключиться к ETH_WS_URL:", RPC_WS_URL)
    exit(1)

# ABI для событий Mint и Burn UniswapV2Pair
PAIR_ABI = [
    {
        "anonymous": False,
        "inputs": [
          {"indexed": True, "internalType": "address", "name": "sender", "type": "address"},
          {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"},
          {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}
        ],
        "name": "Mint",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
          {"indexed": True, "internalType": "address", "name": "sender", "type": "address"},
          {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"},
          {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"},
          {"indexed": True, "internalType": "address", "name": "to", "type": "address"}
        ],
        "name": "Burn",
        "type": "event"
    }
]

# Создаём контракты и фильтры
contracts = []
mint_filters = []
burn_filters = []

for addr in POOL_ADDRESSES:
    c = w3.eth.contract(address=w3.to_checksum_address(addr), abi=PAIR_ABI)
    contracts.append(c)
    # фильтры от latest
    mint_filters.append(c.events.Mint.createFilter(fromBlock="latest"))
    burn_filters.append(c.events.Burn.createFilter(fromBlock="latest"))

print(f"🚀 LPAlert запущен. Пулы:\n  " + "\n  ".join(POOL_ADDRESSES))
print(f"Порог Mint.amount0 ≥ {MIN_LIQ0_THRESHOLD} wei\n")

# Основной цикл
while True:
    for i, addr in enumerate(POOL_ADDRESSES):
        # Mint
        for ev in mint_filters[i].get_new_entries():
            amt0 = Decimal(ev["args"]["amount0"])
            amt1 = Decimal(ev["args"]["amount1"])
            sender = ev["args"]["sender"]
            if amt0 >= MIN_LIQ0_THRESHOLD:
                print(f"💧 MINT LARGE @ {addr}")
                print(f"    sender: {sender}")
                print(f"    amount0: {amt0}  amount1: {amt1}\n")
        # Burn
        for ev in burn_filters[i].get_new_entries():
            amt0 = Decimal(ev["args"]["amount0"])
            amt1 = Decimal(ev["args"]["amount1"])
            sender = ev["args"]["sender"]
            to = ev["args"]["to"]
            print(f"🔥 BURN @ {addr}")
            print(f"    sender: {sender}   to: {to}")
            print(f"    amount0: {amt0}  amount1: {amt1}\n")
    time.sleep(POLL_INTERVAL)
