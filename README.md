# 📈 TFSA Screener V1

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![yfinance](https://img.shields.io/badge/yfinance-6B8E23?style=for-the-badge&logo=yahoo&logoColor=white)
![Quant Finance](https://img.shields.io/badge/Quantitative%20Finance-1A237E?style=for-the-badge&logo=cashapp&logoColor=white)
![Google Colab](https://img.shields.io/badge/Google%20Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white)

> A systematic, rules-based stock screener for Canadian TFSA portfolios — TSX universe only, quarterly rebalancing, no currency risk.

---

## The Idea

Momentum investing — buying assets that have recently outperformed and trimming laggards — is one of the most replicated and academically documented anomalies in empirical finance. This screener operationalizes it for a self-managed TSX portfolio, layering in fundamental quality filters to avoid chasing high-momentum names with deteriorating financials.

The result is a quarterly rebalancing recommendation: **15 primary positions + 4 backup positions**, all priced in CAD, all TSX-listed, all TFSA-eligible.

**Why TSX-only?**
- No USD/CAD currency conversion or dependency
- Full TFSA eligibility on all positions — no foreign withholding tax complications
- Focused universe makes the screener faster and the results more actionable for a Canadian retail investor

---

## Pipeline Overview

The screener runs in 4 sequential stages:

```
~80 TSX tickers
      │
      ▼
Stage 1 — Coarse Filter
(price > $5 CAD, daily dollar volume > $500K)
      │
      ▼
Stage 2 — Fundamental Scoring
(ROE, profit margins, revenue growth, P/E, dividend yield, sector bonus)
      │  Top 80 retained
      ▼
Stage 3 — Momentum Scoring
(90d momentum × 0.7 + 30d momentum × 0.3)
      │
      ▼
Stage 4 — Portfolio Construction
(Top 15 → Primary | Next 4 → Backup)
      │
      ▼
Output: ranked portfolio + CSV export
```

---

## Stage 1 — Coarse Filter

Pulls 1-month price and volume history for each ticker via `yfinance`. Eliminates names that fail either threshold:

| Filter | Threshold | Rationale |
|--------|-----------|-----------|
| Minimum price | $5 CAD | Avoids penny stocks and delisting risk |
| Minimum daily dollar volume | $500K CAD | Ensures reasonable liquidity for retail position sizing |

> Note: TSX liquidity is structurally lower than the S&P 500. The $500K threshold is calibrated accordingly — using the $20M threshold from a US screener would eliminate most of the TSX universe.

Survivors are sorted by dollar volume descending; top 400 pass to Stage 2.

---

## Stage 2 — Fundamental Scoring

Fetches live fundamentals from `yfinance` for each surviving ticker and computes a composite score:

| Factor | Signal | Points |
|--------|--------|--------|
| **Dividend yield** | < 1% | +20 |
| | 1–2% | +15 |
| | 2–3% | +8 |
| | > 3% | 0 |
| **Return on Equity** | > 15% | +15 |
| | 10–15% | +10 |
| | < 0% | −10 |
| **Profit margin** | > 10% | +10 |
| | < −10% | −15 |
| **Revenue growth** | > 15% | +15 |
| | 10–15% | +10 |
| **P/E ratio** | 0 < P/E < 250 | +5 |
| **Sector bonus** | Technology | +15 |
| | Communication Services | +10 |
| | Healthcare | +5 |
| | Utilities | −5 |

The dividend scoring deliberately favors low-yield or no-yield names — consistent with a growth-tilted, TFSA-optimized strategy where capital gains are the primary return driver.

Top 80 scorers pass to Stage 3.

---

## Stage 3 — Momentum Scoring

Computes price momentum over two lookback windows using closing prices from `yfinance` history:

```
momentum_90d  = (price_today - price_90d_ago) / price_90d_ago
momentum_30d  = (price_today - price_30d_ago) / price_30d_ago

combined_momentum = momentum_90d × 0.7 + momentum_30d × 0.3
```

The 70/30 weighting gives more weight to the medium-term trend while incorporating recent acceleration. Tickers with fewer than 90 trading days of history are excluded.

Results are sorted by `combined_momentum` descending.

---

## Stage 4 — Portfolio Construction

| Slot | Selection | Weighting |
|------|-----------|-----------|
| **15 Primary positions** | Top 15 by combined momentum | Equal weight (1/15 each) |
| **4 Backup positions** | Next 4 | Pre-labeled with substitution reasons |

Backup substitution reasons:
1. Position unavailable / halted
2. Earnings announcement imminent
3. Gap > 5% at open
4. Other unforeseen issue

---

## Output

### Console summary
- Full primary portfolio table: ticker, sector, price (CAD), allocation %, number of shares, total CAD
- Backup positions with substitution reasons
- Portfolio stats: average 90d/30d momentum, average dividend yield
- Sector concentration breakdown

### CSV exports

| File | Content |
|------|---------|
| `tfsa_tsx_primary_YYYYMMDD.csv` | 15 primary positions with all scores and metrics |
| `tfsa_tsx_backup_YYYYMMDD.csv` | 4 backup positions |

---

## Historical Simulation Mode

Pass any past date at the prompt to reconstruct what the screener would have recommended on that day:

```
Date de simulation (Entrée = aujourd'hui, ou YYYY-MM-DD pour une date passée) :
➤ 2023-01-01
✅ 2023-01-01
```

**What is historical vs. current:**
- ✅ Historical: closing prices, volume, momentum calculations
- ⚠️ Current: fundamental data (ROE, P/E, margins) — `yfinance` does not provide point-in-time fundamentals

This mode is useful for comparing signal quality across different market regimes, but results should be interpreted with the fundamentals caveat in mind.

---

## Usage

Designed to run in **Google Colab** — no local setup required.

```python
# 1. Open tfsa_tsx_screener.py in Google Colab
# 2. Run all cells
# 3. Enter simulation date when prompted (or press Enter for today)
# 4. Enter capital in CAD when prompted (or press Enter for default 200,000 CAD)
# 5. CSV files auto-download at the end
```

Or call programmatically with custom parameters:

```python
portfolio_full, portfolio_primary, portfolio_backup = run_screener(
    capital=150_000,
    num_holdings=10      # adjust position count
)
```

---

## TSX Universe

The screener covers ~80 TSX-listed tickers across 8 sectors:

| Sector | Example tickers |
|--------|----------------|
| Technology & Software | SHOP.TO, CSU.TO, OTEX.TO, LSPD.TO |
| Financials | RY.TO, TD.TO, MFC.TO, IFC.TO, EQB.TO |
| Energy | CNQ.TO, SU.TO, ENB.TO, TRP.TO |
| Materials & Mining | ABX.TO, WPM.TO, NTR.TO, TECK-B.TO |
| Industrials & Transport | CNR.TO, CP.TO, TFII.TO, WSP.TO |
| Telecoms | BCE.TO, T.TO, RCI-B.TO |
| Consumer & Retail | ATD.TO, L.TO, DOL.TO, GIL.TO |
| Real Estate & Infrastructure | BAM.TO, FTS.TO, BIP-UN.TO |

The universe can be extended by adding `.TO` tickers to the `get_tsx()` function.

---

## Key Design Decisions

**Why equal weighting?**
Equal weighting is simple, transparent, and avoids concentration risk. For a 15-stock portfolio, optimized weighting (e.g., mean-variance) would require return covariance estimates that are noisy at this sample size — adding complexity without reliable improvement.

**Why 90d/30d momentum instead of the academic 12-1 standard?**
The classic 12-1 momentum factor skips the most recent month to avoid short-term reversal. For a quarterly rebalancing cadence, 90d and 30d windows are more actionable and capture regime changes faster — a pragmatic trade-off over academic purity.

**Why filter fundamentals before momentum?**
Applying momentum to a fundamentally-screened subset avoids selecting names that are accelerating into a deteriorating business. Pure momentum strategies can load up on low-quality names during market euphoria — the fundamental gate reduces that risk.

**Why does low dividend yield score higher?**
The scoring preference for low-yield names reflects a growth orientation — high-yield TSX names tend to cluster in sectors (utilities, pipelines, REITs) with lower growth profiles. This is a sector proxy, not a tax argument.

---

## Files

| File | Description |
|------|-------------|
| `tfsa_tsx_screener.py` | Main screener script |
| `tfsa_tsx_primary_YYYYMMDD.csv` | Output: primary positions (generated at runtime) |
| `tfsa_tsx_backup_YYYYMMDD.csv` | Output: backup positions (generated at runtime) |

---

*Rules-based, transparent, and designed to take the emotion out of quarterly rebalancing.*
