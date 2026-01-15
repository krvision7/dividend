# Dividend System Blueprint - Backend Step 2
# 데이터 수집 (loader.py)

## 개요
이 문서는 yfinance를 사용해 배당 데이터를 수집하는 `loader.py`를 구현합니다.

---

## 1. loader.py 생성

`us_market/dividend/loader.py`:

```python
"""
Dividend Data Loader
Fetches dividend data from yfinance and saves to JSON.
- yield: stored as decimal (e.g., 0.055 for 5.5%)
- payments: array of {date, amount} for accurate monthly cashflow
"""
import yfinance as yf
import pandas as pd
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DividendDataLoader:
    def __init__(self, data_dir: str = 'us_market/dividend/data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Load universe seed
        seed_file = os.path.join(data_dir, 'universe_seed.json')
        if os.path.exists(seed_file):
            try:
                with open(seed_file, 'r', encoding='utf-8') as f:
                    seed_data = json.load(f)
                    if isinstance(seed_data, list):
                        self.tickers = [item.get('symbol') for item in seed_data if item.get('symbol')]
                    else:
                        self.tickers = list(seed_data.keys())
                logger.info(f"📋 Loaded {len(self.tickers)} tickers from {seed_file}")
            except Exception as e:
                logger.error(f"Failed to load universe_seed.json: {e}")
                self.tickers = []
        else:
            logger.warning("⚠️ universe_seed.json not found. Using fallback list.")
            self.tickers = ['SCHD', 'JEPI', 'JEPQ', 'DGRO', 'O', 'KO', 'PEP', 'JNJ']

    def fetch_data(self) -> Dict:
        """Fetch dividend data and save to JSON"""
        logger.info("💰 Fetching dividend data...")
        data_map = {}

        for ticker in self.tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info

                # Get price
                price = info.get('currentPrice') or info.get('regularMarketPreviousClose') or 0
                if price is None:
                    price = 0

                # Get dividend history (last 12+ months)
                hist = stock.dividends
                if hist.empty:
                    logger.warning(f"⚠️ {ticker}: No dividend history")
                    continue

                # Make timezone-naive for comparison
                hist.index = hist.index.tz_localize(None)
                one_year_ago = pd.Timestamp.now() - pd.Timedelta(days=370)
                recent_divs = hist[hist.index > one_year_ago]

                # Calculate trailing 12-month yield (decimal)
                ttm_div = float(recent_divs.sum()) if not recent_divs.empty else 0.0
                div_yield = (ttm_div / price) if price > 0 else 0.0

                # Determine frequency
                frequency = len(recent_divs)
                if frequency >= 10:
                    freq_str = "Monthly"
                elif frequency >= 3:
                    freq_str = "Quarterly"
                elif frequency >= 1:
                    freq_str = "Semi-Annual/Annual"
                else:
                    freq_str = "Unknown"

                # Build payments array [{date, amount}]
                payments = []
                for dt, amt in recent_divs.items():
                    payments.append({
                        "date": dt.strftime("%Y-%m-%d"),
                        "amount": float(amt)
                    })

                # Last Payout Amount
                last_amount = float(recent_divs.iloc[-1]) if not recent_divs.empty else 0

                data_map[ticker] = {
                    'name': info.get('shortName', ticker),
                    'sector': info.get('sector', 'ETF'),
                    'price': float(price),
                    'yield': div_yield,  # DECIMAL (e.g., 0.055 for 5.5%)
                    'ttm_dividend': ttm_div,
                    'frequency': freq_str,
                    'last_div': last_amount,
                    'payments': payments,
                    'currency': info.get('currency', 'USD')
                }

                logger.info(f"✅ {ticker}: {div_yield*100:.2f}% ({freq_str}, {len(payments)} payments)")

            except Exception as e:
                logger.error(f"❌ Error fetching {ticker}: {e}")

        # Add Metadata
        data_map['_meta'] = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_tickers': len(data_map),
        }

        # Save to JSON
        output_file = os.path.join(self.data_dir, 'dividend_universe.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data_map, f, ensure_ascii=False, indent=2)

        logger.info(f"💾 Saved {len(data_map)-1} tickers to {output_file}")
        return data_map


if __name__ == "__main__":
    loader = DividendDataLoader()
    loader.fetch_data()
```

---

## 2. 실행 방법

```bash
python us_market/dividend/loader.py
```

### 출력 예시:
```
INFO:__main__:📋 Loaded 214 tickers from us_market/dividend/data/universe_seed.json
INFO:__main__:💰 Fetching dividend data...
INFO:__main__:✅ SCHD: 3.79% (Quarterly, 4 payments)
INFO:__main__:✅ JEPI: 8.15% (Monthly, 12 payments)
...
INFO:__main__:💾 Saved 214 tickers to us_market/dividend/data/dividend_universe.json
```

---

## 3. 생성되는 파일

`us_market/dividend/data/dividend_universe.json`:

```json
{
  "SCHD": {
    "name": "Schwab US Dividend Equity ETF",
    "sector": "ETF",
    "price": 27.47,
    "yield": 0.0379,
    "ttm_dividend": 1.047,
    "frequency": "Quarterly",
    "last_div": 0.278,
    "payments": [
      {"date": "2025-03-26", "amount": 0.249},
      {"date": "2025-06-25", "amount": 0.26},
      {"date": "2025-09-24", "amount": 0.26},
      {"date": "2025-12-10", "amount": 0.278}
    ],
    "currency": "USD"
  },
  "JEPI": {
    "name": "JPMorgan Equity Premium Income ETF",
    "sector": "ETF",
    "price": 57.52,
    "yield": 0.0815,
    "frequency": "Monthly",
    "payments": [
      {"date": "2025-01-06", "amount": 0.39},
      {"date": "2025-02-05", "amount": 0.42},
      ...
    ]
  },
  "_meta": {
    "last_updated": "2025-12-19 09:30:00",
    "total_tickers": 214
  }
}
```

---

## 4. 핵심 개념

### 배당 수익률 계산
```python
# TTM (Trailing 12 Months) 배당금 합계
ttm_div = sum(recent_12_months_dividends)

# 배당 수익률 = TTM 배당금 / 현재 주가
div_yield = ttm_div / current_price  # 0.05 = 5%
```

### 지급 빈도 판단
```python
payments_per_year = len(recent_dividends)

if payments >= 10:    # Monthly
elif payments >= 3:   # Quarterly
elif payments >= 1:   # Semi-Annual/Annual
```

---

## 다음 단계

**BACKEND_STEP3.md**에서 `engine.py`와 최적화 모듈을 구현합니다.
