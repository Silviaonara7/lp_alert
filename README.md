# LPAlert

**LPAlert** — утилита для мониторинга крупных операций Mint/Burn в UniswapV2‑совместимых пулах (Uniswap V2, SushiSwap и др.).  
Сразу увидите, когда «киты» добавляют или удаляют значительную ликвидность.

## Возможности

- Слушает события `Mint` и `Burn` каждого указанного пула через WebSocket‑RPC.  
- При `Mint.amount0` ≥ `MIN_LIQ0_THRESHOLD` (в wei) выводит «китовые» операции.  
- Логирует все `Burn`‑операции для анализа поведения LP.  

## Установка

```bash
git clone https://github.com/<ваш‑аккаунт>/LPAlert.git
cd LPAlert
pip install -r requirements.txt
