# TFSA Tech-Tilted Screener — rebalance trimestriel
# US (S&P 500) + Canada (TSX)

!pip install yfinance pandas numpy requests beautifulsoup4 -q

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


# ── CONFIG ──────────────────────────────────────────────────────────────────

NUM_HOLDINGS      = 15
MIN_PRICE         = 10
MIN_VOLUME        = 20_000_000
MAX_DIVIDEND_YIELD = 0.05

SECTOR_BONUS = {
    'Technology': 15,
    'Communication Services': 10,
    'Healthcare': 5,
    'Consumer Cyclical': 0,
    'Financial Services': 0,
    'Industrials': 0,
    'Consumer Defensive': 0,
    'Energy': 0,
    'Basic Materials': 0,
    'Real Estate': 0,
    'Utilities': -5,
}

GEOGRAPHY_BONUS = 5

DUPLICATE_RULES = {
    'GOOG': 'GOOGL',
    'BRK.B': 'BRK-B',
    'BF.B': 'BF-B',
}


# ── INPUTS ───────────────────────────────────────────────────────────────────

def ask_date():
    print("Date de simulation (Entrée = aujourd'hui, ou YYYY-MM-DD pour une date passée) :")
    while True:
        raw = input("➤ ").strip()
        if raw == "":
            return None
        try:
            d = datetime.strptime(raw, '%Y-%m-%d')
            if d > datetime.now():
                print("Date dans le futur, réessaie.")
                continue
            print(f"✅ {d.strftime('%Y-%m-%d')}")
            return raw
        except ValueError:
            print("Format invalide, utilise YYYY-MM-DD.")


def ask_capital():
    print("Capital en CAD (Entrée = 200 000) :")
    while True:
        raw = input("➤ ").strip()
        if raw == "":
            return 200_000
        try:
            val = float(raw.replace(" ", "").replace(",", "").replace("_", ""))
            if val <= 0:
                print("Doit être positif.")
                continue
            return val
        except ValueError:
            print("Nombre invalide.")


SIMULATION_DATE = ask_date()
CAPITAL_CAD     = ask_capital()


# ── HELPERS DATE / PRIX ──────────────────────────────────────────────────────

def get_sim_date():
    if SIMULATION_DATE:
        return datetime.strptime(SIMULATION_DATE, '%Y-%m-%d')
    return datetime.now()


def get_history(ticker_obj, sim_date, months_back=6):
    """Historique jusqu'à la date simulée."""
    end   = sim_date + timedelta(days=1)
    start = sim_date - timedelta(days=months_back * 31)
    return ticker_obj.history(start=start.strftime('%Y-%m-%d'),
                              end=end.strftime('%Y-%m-%d'))


def get_usdcad(sim_date):
    fallback = 1.35
    try:
        hist = get_history(yf.Ticker('USDCAD=X'), sim_date, months_back=1)
        if hist.empty:
            return fallback
        rate = float(hist['Close'].iloc[-1])
        print(f"💱 USD/CAD au {sim_date.strftime('%Y-%m-%d')} : {rate:.4f}")
        return rate
    except Exception as e:
        print(f"⚠️  Erreur USD/CAD ({e}), fallback {fallback}")
        return fallback


def to_cad(price, ticker, rate):
    """Convertit en CAD si action US."""
    return price if ticker.endswith('.TO') else price * rate


# ── UNIVERS ──────────────────────────────────────────────────────────────────

def get_sp500():
    print("Récupération S&P 500...")
    try:
        import urllib.request
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req) as r:
            tickers = pd.read_html(r.read())[0]['Symbol'].str.replace('.', '-').tolist()
            print(f"  {len(tickers)} tickers S&P 500")
            return tickers
    except Exception as e:
        print(f"  Wikipedia KO ({e}), utilisation liste backup")
        return [
            "AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA","AVGO","ORCL","CRM",
            "ADBE","CSCO","ACN","AMD","INTC","QCOM","INTU","TXN","AMAT","MU",
            "LRCX","KLAC","SNPS","CDNS","MRVL","FTNT","PANW","CRWD","ZS","DDOG",
            "NET","SNOW","NOW","TEAM","WDAY","HUBS","ZM","DOCU","TWLO","PLTR",
            "RBLX","U","COIN","NFLX","DIS","CMCSA","VZ","T","TMUS","CHTR",
            "EA","TTWO","ROKU","PINS","SNAP","HD","NKE","MCD","SBUX","TGT",
            "LOW","TJX","LULU","BKNG","MAR","ABNB","DASH","UBER","LYFT","GM","F",
            "UNH","JNJ","LLY","ABBV","MRK","TMO","ABT","DHR","PFE","AMGN",
            "GILD","VRTX","REGN","ISRG","MRNA","BNTX","ILMN","JPM","V","MA",
            "BAC","WFC","GS","MS","BLK","SCHW","AXP","C","USB","PNC","TFC",
            "BK","SYF","COF","DFS","CAT","BA","HON","UPS","RTX","LMT","DE",
            "UNP","GE","WMT","PG","COST","KO","PEP","PM","MO","CL","KMB",
            "XOM","CVX","COP","SLB","EOG","MPC","PSX","VLO","LIN","APD",
            "ECL","SHW","NEM","FCX","NUE","PLD","AMT","EQIX","SPG","O","DLR",
            "NEE","DUK","SO","D","AEP","EXC","SRE",
        ]


def get_tsx():
    return [
        "SHOP.TO","RY.TO","TD.TO","BNS.TO","BMO.TO","CM.TO",
        "MFC.TO","SLF.TO","GWO.TO","IFC.TO",
        "CNQ.TO","SU.TO","IMO.TO","CVE.TO","TRP.TO","ENB.TO",
        "ABX.TO","NTR.TO","FM.TO","TECK-B.TO","WPM.TO","FNV.TO","K.TO",
        "CNR.TO","CP.TO","TFII.TO","CSU.TO","WCN.TO",
        "BCE.TO","T.TO","RCI-B.TO",
        "L.TO","ATD.TO","QSR.TO","DOL.TO","MG.TO",
        "BAM.TO","FTS.TO","EMA.TO","AQN.TO",
        "WELL.TO","CCL-B.TO","BIP-UN.TO",
    ]


def deduplicate(tickers):
    clean, seen = [], set()
    for t in tickers:
        preferred = DUPLICATE_RULES.get(t, t)
        if preferred not in seen:
            clean.append(preferred)
            seen.add(preferred)
    return clean


def build_universe():
    us = deduplicate(get_sp500())
    ca = get_tsx()
    print(f"Univers total : {len(us)} US + {len(ca)} CA = {len(us)+len(ca)} tickers")
    return us + ca, us, ca


# ── ÉTAPE 1 : FILTRE COARSE ──────────────────────────────────────────────────

def coarse_filter(tickers, sim_date, usdcad):
    print(f"\nFiltre coarse (prix & volume) — {sim_date.strftime('%Y-%m-%d')}...")
    passed, failed = [], 0

    for i, ticker in enumerate(tickers):
        if i % 50 == 0:
            print(f"  {i}/{len(tickers)}")
        try:
            hist = get_history(yf.Ticker(ticker), sim_date, months_back=1)
            if hist.empty:
                failed += 1; continue

            price_native = float(hist['Close'].iloc[-1])
            price_cad    = to_cad(price_native, ticker, usdcad)
            avg_vol      = float(hist.tail(10)['Volume'].mean())
            dollar_vol   = price_cad * avg_vol

            if price_cad > MIN_PRICE and dollar_vol > MIN_VOLUME:
                passed.append({
                    'ticker':        ticker,
                    'price':         price_cad,
                    'price_native':  price_native,
                    'currency':      'CAD' if ticker.endswith('.TO') else 'USD→CAD',
                    'avg_volume':    avg_vol,
                    'dollar_volume': dollar_vol,
                })
            else:
                failed += 1
        except Exception:
            failed += 1

    print(f"  Passé: {len(passed)} | Échoué: {failed}")
    df = pd.DataFrame(passed).sort_values('dollar_volume', ascending=False)
    return df.head(400)


# ── ÉTAPE 2 : SCORING FONDAMENTAL ────────────────────────────────────────────

def fine_filter(coarse_df, ca_tickers, sim_date):
    print(f"\nScoring fondamental — {sim_date.strftime('%Y-%m-%d')}...")
    rows = []

    for _, row in coarse_df.iterrows():
        ticker = row['ticker']
        try:
            info  = yf.Ticker(ticker).info
            score = 0
            d     = {'ticker': ticker, 'price': row['price']}

            is_ca          = ticker in ca_tickers
            d['country']   = 'Canada' if is_ca else 'USA'
            d['geo_bonus'] = GEOGRAPHY_BONUS if is_ca else 0
            score         += d['geo_bonus']

            sector           = info.get('sector', 'Unknown')
            d['sector']      = sector
            d['sector_bonus'] = SECTOR_BONUS.get(sector, 0)
            score           += d['sector_bonus']

            div_yield           = info.get('dividendYield', 0) or 0
            d['dividend_yield'] = div_yield
            if div_yield < 0.01:   score += 20; d['div_bonus'] = 20
            elif div_yield < 0.02: score += 15; d['div_bonus'] = 15
            elif div_yield < 0.03: score += 8;  d['div_bonus'] = 8
            else:                               d['div_bonus'] = 0

            roe     = info.get('returnOnEquity')
            d['roe'] = roe
            if roe:
                if roe > 0.15:   score += 15; d['roe_bonus'] = 15
                elif roe > 0.10: score += 10; d['roe_bonus'] = 10
                elif roe < 0:    score -= 10; d['roe_bonus'] = -10
                else:                         d['roe_bonus'] = 0
            else:
                d['roe_bonus'] = 0

            margin           = info.get('profitMargins')
            d['profit_margin'] = margin
            if margin:
                if margin > 0.10:    score += 10; d['margin_bonus'] = 10
                elif margin < -0.10: score -= 15; d['margin_bonus'] = -15
                else:                             d['margin_bonus'] = 0
            else:
                d['margin_bonus'] = 0

            rev_growth           = info.get('revenueGrowth')
            d['revenue_growth']  = rev_growth
            if rev_growth:
                if rev_growth > 0.15:   score += 15; d['growth_bonus'] = 15
                elif rev_growth > 0.10: score += 10; d['growth_bonus'] = 10
                else:                               d['growth_bonus'] = 0
            else:
                d['growth_bonus'] = 0

            pe        = info.get('trailingPE')
            d['pe_ratio'] = pe
            d['pe_bonus'] = 5 if (pe and 0 < pe < 250) else 0
            score        += d['pe_bonus']

            d['fundamental_score'] = score
            rows.append(d)
        except Exception:
            continue

    df = pd.DataFrame(rows).sort_values('fundamental_score', ascending=False)
    print(f"  {len(df)} actions scorées")
    print(df[['ticker','country','sector','fundamental_score','dividend_yield']].head(10).to_string())
    return df.head(80)


# ── ÉTAPE 3 : MOMENTUM ───────────────────────────────────────────────────────

def calc_momentum(fine_df, sim_date, usdcad):
    print(f"\nCalcul momentum — {sim_date.strftime('%Y-%m-%d')}...")
    rows = []

    for _, row in fine_df.iterrows():
        ticker = row['ticker']
        try:
            hist = get_history(yf.Ticker(ticker), sim_date, months_back=6)
            if len(hist) < 90:
                continue

            cur   = float(hist['Close'].iloc[-1])
            p90   = float(hist['Close'].iloc[-90])
            p30   = float(hist['Close'].iloc[-30])

            mom90    = (cur - p90) / p90
            mom30    = (cur - p30) / p30
            mom_comb = mom90 * 0.7 + mom30 * 0.3

            rows.append({
                'ticker':               ticker,
                'country':              row['country'],
                'currency':             'CAD' if ticker.endswith('.TO') else 'USD→CAD',
                'current_price':        to_cad(cur, ticker, usdcad),
                'current_price_native': cur,
                'momentum_90d':         mom90,
                'momentum_30d':         mom30,
                'combined_momentum':    mom_comb,
                'fundamental_score':    row['fundamental_score'],
                'sector':               row['sector'],
                'dividend_yield':       row['dividend_yield'],
            })
        except Exception:
            continue

    df = pd.DataFrame(rows).sort_values('combined_momentum', ascending=False)
    print(f"  {len(df)} actions avec momentum calculé")
    return df


# ── ÉTAPE 4 : SÉLECTION FINALE ───────────────────────────────────────────────

def select_portfolio(momentum_df, n=NUM_HOLDINGS):
    df = momentum_df.head(n + 4).copy()
    df['position_type']      = ['Primary'] * n + ['Backup'] * 4
    df['target_weight']      = 0.0
    df.loc[df['position_type'] == 'Primary', 'target_weight'] = 1.0 / n
    df['target_weight_pct']  = df['target_weight'] * 100
    return df


# ── AFFICHAGE ────────────────────────────────────────────────────────────────

def display_results(portfolio_df, sim_date, capital, usdcad):
    primary = portfolio_df[portfolio_df['position_type'] == 'Primary'].copy()
    backup  = portfolio_df[portfolio_df['position_type'] == 'Backup'].copy()

    primary['position_value_cad']   = capital * primary['target_weight']
    primary['num_shares']           = (primary['position_value_cad'] / primary['current_price']).astype(int)
    primary['total_cad']            = primary['num_shares'] * primary['current_price']
    primary['actual_allocation_pct'] = primary['total_cad'] / capital * 100

    label  = sim_date.strftime('%Y-%m-%d')
    is_sim = SIMULATION_DATE is not None

    print("\n" + "="*105)
    print("PORTFOLIO RECOMMANDÉ — TFSA TECH-TILTED (US + CANADA)")
    if is_sim:
        print(f"SIMULATION HISTORIQUE — {label}")
    print("="*105)
    print(f"\nCapital        : {capital:,.0f} CAD")
    print(f"Taux USD/CAD   : {usdcad:.4f}")
    print(f"Date           : {label}" + (" (historique)" if is_sim else ""))
    print(f"Positions      : {len(primary)} primaires + {len(backup)} backup")
    print(f"Montant/pos    : {capital/len(primary):,.0f} CAD ({100/len(primary):.2f}%)")

    print("\n" + "-"*105)
    print("POSITIONS PRIMAIRES — montants en CAD")
    print("-"*105)
    print(f"{'#':<3} {'Ticker':<10} {'Pays':<4} {'Devise':<9} {'Secteur':<22} {'Prix CAD':<11} {'Alloc%':<9} {'Actions':<10} {'Total CAD'}")
    print("-"*105)

    for i, (_, r) in enumerate(primary.iterrows()):
        flag = '🇨🇦' if r['country'] == 'Canada' else '🇺🇸'
        print(f"{i+1:<3} {r['ticker']:<10} {flag:<4} {r.get('currency','CAD'):<9} {r['sector'][:20]:<22} "
              f"${r['current_price']:<10.2f} {r['actual_allocation_pct']:<8.2f}% "
              f"{r['num_shares']:<10.0f} ${r['total_cad']:,.0f}")

    print("-"*105)
    total_inv = primary['total_cad'].sum()
    cash      = capital - total_inv
    print(f"\nInvesti  : {total_inv:,.0f} CAD ({total_inv/capital*100:.1f}%)")
    print(f"Cash     : {cash:,.0f} CAD ({cash/capital*100:.1f}%)")

    print("\n" + "-"*105)
    print("BACKUP (utiliser si une position primaire est problématique)")
    print("-"*105)
    reasons = ["Position inachetable", "Earnings imminent", "Gap >5%", "Autre imprévu"]
    for i, (_, r) in enumerate(backup.iterrows()):
        flag = '🇨🇦' if r['country'] == 'Canada' else '🇺🇸'
        print(f"{i+1:<3} {r['ticker']:<10} {flag:<4} {r.get('currency','CAD'):<9} {r['sector'][:20]:<22} "
              f"${r['current_price']:<10.2f}  mom90={r['momentum_90d']*100:.1f}%  → {reasons[i]}")

    print("\nStats positions primaires :")
    print(f"  Momentum moyen 90j : {primary['momentum_90d'].mean()*100:.2f}%")
    print(f"  Momentum moyen 30j : {primary['momentum_30d'].mean()*100:.2f}%")
    print(f"  Dividende moyen    : {primary['dividend_yield'].mean()*100:.2f}%")

    print("\nRépartition géographique :")
    for country, w in primary.groupby('country')['actual_allocation_pct'].sum().sort_values(ascending=False).items():
        flag = '🇨🇦' if country == 'Canada' else '🇺🇸'
        print(f"  {flag} {country} : {w:.2f}%")

    print("\nRépartition sectorielle :")
    for sector, w in primary.groupby('sector')['actual_allocation_pct'].sum().sort_values(ascending=False).items():
        print(f"  {sector:<30} : {w:.2f}%")

    return primary, backup


# ── EXPORT ───────────────────────────────────────────────────────────────────

def export_results(portfolio_df, sim_date, usdcad):
    date_str = sim_date.strftime('%Y%m%d')
    cols_rename = {
        'ticker': 'Ticker', 'country': 'Pays', 'currency': 'Devise',
        'sector': 'Secteur', 'current_price': 'Prix CAD',
        'current_price_native': 'Prix Natif', 'target_weight_pct': 'Poids %',
        'momentum_90d': 'Momentum 90j', 'momentum_30d': 'Momentum 30j',
        'combined_momentum': 'Momentum Combiné',
        'dividend_yield': 'Dividende %', 'fundamental_score': 'Score Fondamental',
    }
    for label in ('Primary', 'Backup'):
        df = portfolio_df[portfolio_df['position_type'] == label].copy()
        df = df[[c for c in cols_rename if c in df.columns]].rename(columns=cols_rename)
        df['Taux USD/CAD'] = usdcad
        fname = f"tfsa_portfolio_{label.lower()}_{date_str}.csv"
        df.to_csv(fname, index=False)
        print(f"Exporté : {fname}")


# ── MAIN ─────────────────────────────────────────────────────────────────────

def run_screener(capital=None, num_holdings=NUM_HOLDINGS):
    capital  = capital or CAPITAL_CAD
    sim_date = get_sim_date()

    print("="*80)
    print("TFSA TECH-TILTED SCREENER — US + CANADA")
    print(f"Date    : {sim_date.strftime('%Y-%m-%d')}" +
          (" (simulation historique)" if SIMULATION_DATE else ""))
    print(f"Capital : {capital:,.0f} CAD  |  Positions : {num_holdings} + 4 backup")
    print("="*80)

    if SIMULATION_DATE:
        print("\nNote : prix & momentum sont historiques ; "
              "les fondamentaux (ROE, P/E…) reflètent les valeurs actuelles de yfinance.\n")

    usdcad = get_usdcad(sim_date)

    all_tickers, us_tickers, ca_tickers = build_universe()
    coarse_df    = coarse_filter(all_tickers, sim_date, usdcad)
    fine_df      = fine_filter(coarse_df, ca_tickers, sim_date)
    momentum_df  = calc_momentum(fine_df, sim_date, usdcad)
    portfolio_df = select_portfolio(momentum_df, num_holdings)
    primary, backup = display_results(portfolio_df, sim_date, capital, usdcad)
    export_results(portfolio_df, sim_date, usdcad)

    return portfolio_df, primary, backup


if __name__ == "__main__":
    portfolio_full, portfolio_primary, portfolio_backup = run_screener()

    from google.colab import files
    date_str = get_sim_date().strftime('%Y%m%d')
    files.download(f'tfsa_portfolio_primary_{date_str}.csv')
    files.download(f'tfsa_portfolio_backup_{date_str}.csv')
