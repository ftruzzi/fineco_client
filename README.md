A Python client for Fineco bank.

Does not have many features for now, as I built it to automate operations that can't be done on the website. I wanted to send automatic international bank transfers and receive an alert when parts of my portfolio were green.

The way I use this is with cron scripts which use this client to automate operations.

# Installation

Clone the repo, install poetry and run `poetry install`

# Supported features

- Perform international bank transfers (EUR only)
- Get total profit/loss for portfolio items

# Usage

Also see `/examples` folder.

```python
from fineco_client import FinecoClient, FinecoBankTransfer

client = FinecoClient(username="USERNAME", password="PASSWORD")
```

## Sending a transfer

```python
transfer = FinecoBankTransfer(
    amount=1.23,
    description="Test transfer",
    recipient_country="Germany",
    recipient_iban="<IBAN HERE>",
    recipient_name="Topo Gigio",
)
client.send_transfer(transfer)
```

At this point you will receive a notification on your 2FA device to confirm the transaction through your app.

## Checking your portfolio

```python
>>> portfolio = client.get_portfolio()
>>> portfolio[0]
<FinecoPortfolioItem: {'currency': 'USD', 'description': 'SOFI TECH', 'isin': 'US83406F1021', 'quantity': 430, 'ticker': 'SOFI.O', 'total_profit': -752.54}>
```

# Donations

Just in case you want to say thanks :)

**BTC**: 3Kdyv75GpzwZ1b19QECwr3znsjSSkoRAVq

**ETH**: 0x1Af2121BaF1795Ce3685893d89E5eC6e6E1DC510

**DOGE**: DLdbw36tgSqK52njimJKsitCtVg1D4n8t9