# TFSA_Screener-V1
Momentum-based stock screener for TFSA/RRSP portfolios. Covers S&amp;P 500 + TSX, outputs 15 positions sized to your capital. Runs in Google Colab.

## How it works

The script runs ~550 tickers (S&P 500 + ~40 large Canadian caps) through a 3-step pipeline:

1. **Coarse filter** — drops anything too small or illiquid (price < $10 CAD, dollar volume < $20M CAD/day)
2. **Fundamental score** — awards points based on sector, dividend yield, ROE, margins, revenue growth, and P/E. Small bonus for Canadian stocks (tax efficiency in a TFSA)
3. **Momentum** — calculates a combined 90d/30d score (70%/30% weight) on historical prices. Final ranking is momentum-driven

Output: 15 primary positions + 4 backups, with share counts calculated automatically based on the capital you enter. All prices are converted to CAD using a live USD/CAD rate from yfinance.

---

## Usage

The script is meant to run in **Google Colab**. Just paste the file into a notebook and run it.

At startup, two questions are asked:

```
Simulation date (Enter = today, or YYYY-MM-DD for a past date):
Capital in CAD (Enter = 200,000):
```

- **Date**: leave blank for a live screener. Enter a past date to see what the screener would have picked at that point in time — useful for sanity-checking the logic on historical periods
- **Capital**: total amount to invest, in CAD

At the end, two CSVs are exported automatically:
- `tfsa_portfolio_primary_YYYYMMDD.csv`
- `tfsa_portfolio_backup_YYYYMMDD.csv`

---

## Configurable parameters

A few constants at the top of the file that are easy to tweak:

| Parameter | Default | Description |
|---|---|---|
| `NUM_HOLDINGS` | 15 | Number of primary positions |
| `MIN_PRICE` | 10 CAD | Minimum share price |
| `MIN_VOLUME` | 20,000,000 | Minimum daily dollar volume (CAD) |
| `SECTOR_BONUS` | see code | Extra points by sector |
| `GEOGRAPHY_BONUS` | 5 | Bonus for `.TO` tickers |

---

## Known limitations

- **Fundamental data**: yfinance always returns *current* values for metrics like ROE, P/E, and revenue growth. In historical simulation mode, only prices and momentum are truly historical. It's an approximation, not a clean backtest.
- **Wikipedia scraping**: the S&P 500 list is scraped from Wikipedia. If that request fails, the script falls back to a hardcoded list of ~150 tickers.
- **Runtime**: the script makes a lot of sequential yfinance calls. Expect 15–25 minutes for a full run on Colab.

---

## Dependencies

```
yfinance
pandas
numpy
requests
beautifulsoup4
```

All installed automatically at the top of the script (`!pip install ...`).

---

## Disclaimer

This is not financial advice. The output is meant to inform a decision, not make it for you. Always check earnings dates before buying — that's what the backup positions are there for.
