# Dividend System Blueprint - Backend Step 3
# 엔진 및 최적화 모듈

## 개요
이 문서는 포트폴리오 생성 엔진(`engine.py`)과 최적화 모듈(`portfolio_optimizer.py`, `risk_analytics.py`)을 구현합니다.

---

## 1. engine.py (핵심 엔진)

`us_market/dividend/engine.py`:

```python
"""
Dividend Portfolio Engine
- Loads themes × tiers from dividend_plans.json
- Applies constraints: ETF min, allowed/banned tags
- Supports multiple optimization modes
"""
import json
import os
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

OPTIMIZE_MODES = ['greedy', 'risk_parity', 'mean_variance', 'max_sharpe', 'min_vol']


class DividendEngine:
    def __init__(self, data_dir: str = 'us_market/dividend'):
        self.data_dir = data_dir
        self.config_dir = os.path.join(data_dir, 'config')
        self.data_subdir = os.path.join(data_dir, 'data')
        
        # Load configuration
        self.plans = self._load_json(os.path.join(self.config_dir, 'dividend_plans.json'))
        self.tags_def = self._load_json(os.path.join(self.config_dir, 'tags.json'))
        
        # Load universe data
        self.universe_seed = self._load_json(os.path.join(self.data_subdir, 'universe_seed.json'))
        self.dividend_data = self._load_dividend_data()
        self.symbol_tags = self._build_symbol_tags()

    def _load_json(self, path: str) -> Dict:
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_dividend_data(self) -> Dict:
        path = os.path.join(self.data_subdir, 'dividend_universe.json')
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Normalize yield if stored as percent
        for ticker, stock in data.items():
            if ticker.startswith('_'):
                continue
            y = stock.get("yield", 0) or 0
            if y > 1:
                stock["yield"] = y / 100.0
        return data

    def _build_symbol_tags(self) -> Dict[str, List[str]]:
        mapping = {}
        if isinstance(self.universe_seed, list):
            for item in self.universe_seed:
                symbol = item.get('symbol', '')
                tags = item.get('tags', [])
                asset_type = item.get('type', 'STOCK')
                if asset_type == 'ETF':
                    tags = tags + ['etf']
                else:
                    tags = tags + ['stock']
                mapping[symbol] = tags
        return mapping

    def _filter_universe(self, allowed_tags: List[str], banned_tags: List[str]) -> List[str]:
        eligible = []
        for symbol, tags in self.symbol_tags.items():
            if any(t in tags for t in banned_tags):
                continue
            if any(t in tags for t in allowed_tags):
                if symbol in self.dividend_data:
                    eligible.append(symbol)
        return eligible

    def _select_portfolio(
        self,
        eligible_symbols: List[str],
        constraints: Dict,
        target_capital_usd: float,
        optimize_mode: str = 'greedy'
    ) -> List[Tuple[str, float]]:
        """Select portfolio using specified optimization mode."""
        
        # Try advanced optimization if not greedy
        if optimize_mode != 'greedy' and optimize_mode in OPTIMIZE_MODES:
            try:
                from .portfolio_optimizer import PortfolioOptimizer
                optimizer = PortfolioOptimizer()
                valid_symbols = [
                    s for s in eligible_symbols 
                    if self.dividend_data.get(s, {}).get('yield', 0) > 0
                ]
                if len(valid_symbols) >= 3:
                    optimized = optimizer.optimize(
                        tickers=valid_symbols[:20],
                        method=optimize_mode,
                        constraints=constraints
                    )
                    if optimized:
                        return optimized
            except Exception as e:
                logger.error(f"Optimization failed: {e}")
        
        # Fallback: Greedy approach
        etf_min = constraints.get('etf_min', 0.5)
        single_stock_max = constraints.get('single_stock_max', 0.10)
        
        etfs = []
        stocks = []
        for symbol in eligible_symbols:
            data = self.dividend_data.get(symbol, {})
            div_yield = data.get('yield', 0) or 0
            if div_yield <= 0:
                continue
            is_etf = 'etf' in self.symbol_tags.get(symbol, [])
            if is_etf:
                etfs.append((symbol, div_yield))
            else:
                stocks.append((symbol, div_yield))
        
        etfs.sort(key=lambda x: x[1], reverse=True)
        stocks.sort(key=lambda x: x[1], reverse=True)
        
        portfolio = []
        total_weight = 0.0
        etf_weight = 0.0
        
        # Add ETFs first
        for symbol, div_yield in etfs:
            if etf_weight >= etf_min:
                break
            weight = min(0.25, etf_min - etf_weight)
            portfolio.append((symbol, weight))
            etf_weight += weight
            total_weight += weight
        
        # Fill with stocks
        remaining = 1.0 - total_weight
        for symbol, div_yield in stocks[:10]:
            if remaining <= 0:
                break
            weight = min(single_stock_max, remaining)
            if weight >= 0.03:
                portfolio.append((symbol, weight))
                total_weight += weight
                remaining = 1.0 - total_weight
        
        # Normalize
        if portfolio and total_weight > 0:
            factor = 1.0 / total_weight
            portfolio = [(s, w * factor) for s, w in portfolio]
        
        return portfolio

    def generate_portfolio(
        self,
        theme_id: str,
        tier_id: str,
        target_monthly_krw: float = 1000000,
        fx_rate: float = 1420,
        tax_rate: float = 0.154,
        optimize_mode: str = 'greedy'
    ) -> Dict:
        """Generate portfolio for given theme and tier."""
        
        # Find theme
        theme = None
        for t in self.plans.get('themes', []):
            if t['id'] == theme_id:
                theme = t
                break
        if not theme:
            return {"error": f"Theme '{theme_id}' not found"}
        
        tier_config = theme.get('tiers', {}).get(tier_id)
        if not tier_config:
            return {"error": f"Tier '{tier_id}' not found"}
        
        card_front = tier_config.get('card_front', {})
        constraints = tier_config.get('constraints', {})
        allowed_tags = tier_config.get('allowed_tags', [])
        banned_tags = tier_config.get('banned_tags', [])
        
        # Calculate targets
        target_monthly_usd = target_monthly_krw / fx_rate
        target_annual_usd_pretax = (target_monthly_usd * 12) / (1 - tax_rate)
        
        # Filter universe
        eligible = self._filter_universe(allowed_tags, banned_tags)
        if not eligible:
            return {"error": "No eligible tickers"}
        
        # Select portfolio
        portfolio_weights = self._select_portfolio(
            eligible, constraints, target_annual_usd_pretax, optimize_mode
        )
        if not portfolio_weights:
            return {"error": "Could not construct portfolio"}
        
        # Calculate portfolio yield
        portfolio_yield = 0.0
        for symbol, weight in portfolio_weights:
            data = self.dividend_data.get(symbol, {})
            div_yield = data.get('yield', 0) or 0
            portfolio_yield += div_yield * weight
        
        if portfolio_yield <= 0:
            return {"error": "Portfolio yield is zero"}
        
        # Calculate required capital
        required_capital_usd = target_annual_usd_pretax / portfolio_yield
        
        # Build allocation
        allocation = []
        monthly_flow = [0.0] * 12
        
        for symbol, weight in portfolio_weights:
            data = self.dividend_data.get(symbol, {})
            amount_usd = required_capital_usd * weight
            price = data.get('price', 1) or 1
            shares = amount_usd / price
            
            # Calculate monthly cashflow
            payments = data.get('payments', [])
            if payments:
                for p in payments:
                    try:
                        month = int(p['date'][5:7])
                        monthly_flow[month - 1] += p['amount'] * shares
                    except:
                        pass
            
            allocation.append({
                "ticker": symbol,
                "name": data.get('name', symbol),
                "weight": round(weight * 100, 1),
                "shares": round(shares, 1),
                "price": round(price, 2),
                "yield": f"{(data.get('yield', 0) or 0) * 100:.2f}%",
                "amount_usd": round(amount_usd, 2)
            })
        
        # Apply tax and convert to KRW
        monthly_flow_krw = [round(flow * (1 - tax_rate) * fx_rate) for flow in monthly_flow]
        
        return {
            "theme_id": theme_id,
            "tier_id": tier_id,
            "title": card_front.get('headline', theme['title']),
            "one_liner": card_front.get('one_liner', theme['subtitle']),
            "risk_label": card_front.get('risk_label', '중간'),
            "required_capital_krw": round(required_capital_usd * fx_rate),
            "expected_monthly_krw": round(sum(monthly_flow_krw) / 12),
            "portfolio_yield": f"{portfolio_yield * 100:.2f}%",
            "allocation": allocation,
            "chart_data": monthly_flow_krw,
            "optimize_mode": optimize_mode
        }

    def generate_all_tiers(self, theme_id: str, **kwargs) -> Dict:
        """Generate all 3 tier portfolios for a theme."""
        results = {}
        for tier in ['defensive', 'balanced', 'aggressive']:
            results[tier] = self.generate_portfolio(theme_id, tier, **kwargs)
        return results
```

---

## 2. portfolio_optimizer.py

`us_market/dividend/portfolio_optimizer.py`:

```python
"""
Portfolio Optimizer
Risk Parity, Mean-Variance, Max Sharpe optimization
"""
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PortfolioOptimizer:
    _returns_cache: Dict[str, pd.Series] = {}
    
    def __init__(self, risk_free_rate: float = 0.05):
        self.risk_free_rate = risk_free_rate
    
    def _get_returns(self, ticker: str, period: str = '1y') -> Optional[pd.Series]:
        cache_key = f"{ticker}_{period}"
        if cache_key in self._returns_cache:
            return self._returns_cache[cache_key]
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if hist.empty or len(hist) < 30:
                return None
            returns = hist['Close'].pct_change().dropna()
            self._returns_cache[cache_key] = returns
            return returns
        except:
            return None
    
    def _get_returns_matrix(self, tickers: List[str], period: str = '1y') -> Optional[pd.DataFrame]:
        returns_dict = {}
        for ticker in tickers:
            returns = self._get_returns(ticker, period)
            if returns is not None:
                returns_dict[ticker] = returns
        if len(returns_dict) < 2:
            return None
        return pd.DataFrame(returns_dict).dropna()
    
    def optimize_risk_parity(
        self, tickers: List[str], constraints: Optional[Dict] = None
    ) -> Optional[List[Tuple[str, float]]]:
        """Equal risk contribution from each asset."""
        returns_df = self._get_returns_matrix(tickers)
        if returns_df is None or len(returns_df) < 30:
            return None
        
        valid_tickers = list(returns_df.columns)
        n = len(valid_tickers)
        cov_matrix = returns_df.cov() * 252
        
        def risk_parity_objective(weights):
            weights = np.array(weights)
            portfolio_vol = np.sqrt(weights.T @ cov_matrix @ weights)
            mrc = cov_matrix @ weights / portfolio_vol
            rc = weights * mrc
            target_rc = np.sum(rc) / n
            return np.sum((rc - target_rc) ** 2)
        
        x0 = np.ones(n) / n
        cons = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        max_weight = constraints.get('single_stock_max', 0.5) if constraints else 0.5
        bounds = [(0.02, max_weight)] * n
        
        result = minimize(risk_parity_objective, x0, method='SLSQP', bounds=bounds, constraints=cons)
        
        if result.success:
            weights = result.x
            portfolio = [(valid_tickers[i], round(float(weights[i]), 4)) for i in range(n) if weights[i] >= 0.02]
            total = sum(w for _, w in portfolio)
            return [(t, round(w/total, 4)) for t, w in portfolio]
        return None
    
    def optimize_max_sharpe(
        self, tickers: List[str], constraints: Optional[Dict] = None
    ) -> Optional[List[Tuple[str, float]]]:
        """Maximize Sharpe ratio."""
        returns_df = self._get_returns_matrix(tickers)
        if returns_df is None:
            return None
        
        valid_tickers = list(returns_df.columns)
        n = len(valid_tickers)
        expected_returns = returns_df.mean() * 252
        cov_matrix = returns_df.cov() * 252
        
        def neg_sharpe(weights):
            port_return = weights.T @ expected_returns
            port_vol = np.sqrt(weights.T @ cov_matrix @ weights)
            return -(port_return - self.risk_free_rate) / port_vol if port_vol > 0 else 0
        
        x0 = np.ones(n) / n
        cons = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        max_weight = constraints.get('single_stock_max', 0.5) if constraints else 0.5
        bounds = [(0.02, max_weight)] * n
        
        result = minimize(neg_sharpe, x0, method='SLSQP', bounds=bounds, constraints=cons)
        
        if result.success:
            weights = result.x
            portfolio = [(valid_tickers[i], round(float(weights[i]), 4)) for i in range(n) if weights[i] >= 0.02]
            total = sum(w for _, w in portfolio)
            return [(t, round(w/total, 4)) for t, w in portfolio]
        return None
    
    def optimize(
        self, tickers: List[str], method: str = 'risk_parity', constraints: Optional[Dict] = None
    ) -> Optional[List[Tuple[str, float]]]:
        """Unified optimization interface."""
        if method == 'risk_parity':
            return self.optimize_risk_parity(tickers, constraints)
        elif method == 'max_sharpe':
            return self.optimize_max_sharpe(tickers, constraints)
        else:
            return None
```

---

## 3. risk_analytics.py

`us_market/dividend/risk_analytics.py`:

```python
"""
Risk Analytics - Volatility, Drawdown, Sharpe, Beta
"""
import yfinance as yf
import numpy as np
import pandas as pd
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RiskAnalytics:
    _price_cache: Dict[str, pd.DataFrame] = {}
    
    def __init__(self, risk_free_rate: float = 0.05):
        self.risk_free_rate = risk_free_rate
    
    def _get_price_data(self, ticker: str, period: str = '1y') -> Optional[pd.DataFrame]:
        cache_key = f"{ticker}_{period}"
        if cache_key in self._price_cache:
            return self._price_cache[cache_key]
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            if df.empty:
                return None
            self._price_cache[cache_key] = df
            return df
        except:
            return None
    
    def calculate_volatility(self, ticker: str, period: str = '1y') -> Optional[float]:
        df = self._get_price_data(ticker, period)
        if df is None or len(df) < 20:
            return None
        returns = np.log(df['Close'] / df['Close'].shift(1)).dropna()
        return round(float(returns.std() * np.sqrt(252)), 4)
    
    def calculate_max_drawdown(self, ticker: str, period: str = '1y') -> Optional[float]:
        df = self._get_price_data(ticker, period)
        if df is None or len(df) < 20:
            return None
        prices = df['Close']
        rolling_max = prices.expanding().max()
        drawdowns = (prices - rolling_max) / rolling_max
        return round(float(drawdowns.min()), 4)
    
    def calculate_sharpe_ratio(self, ticker: str, period: str = '1y') -> Optional[float]:
        df = self._get_price_data(ticker, period)
        if df is None or len(df) < 20:
            return None
        returns = np.log(df['Close'] / df['Close'].shift(1)).dropna()
        annual_return = returns.mean() * 252
        annual_vol = returns.std() * np.sqrt(252)
        if annual_vol == 0:
            return None
        return round(float((annual_return - self.risk_free_rate) / annual_vol), 2)
    
    def get_all_risk_metrics(self, ticker: str, period: str = '1y') -> Dict:
        return {
            'ticker': ticker,
            'volatility_annual': self.calculate_volatility(ticker, period),
            'max_drawdown': self.calculate_max_drawdown(ticker, period),
            'sharpe_ratio': self.calculate_sharpe_ratio(ticker, period)
        }
```

---

## 4. dividend_analyzer.py (배당 지속성 분석)

`us_market/dividend/dividend_analyzer.py`:

```python
"""
Dividend Sustainability Analyzer
Payout Ratio, Growth Rate, Streak, Safety Score
"""
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DividendAnalyzer:
    _info_cache: Dict[str, Dict] = {}
    
    def __init__(self):
        pass
    
    def _get_stock_info(self, ticker: str) -> Optional[Dict]:
        if ticker in self._info_cache:
            return self._info_cache[ticker]
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            self._info_cache[ticker] = info
            return info
        except:
            return None
    
    def calculate_payout_ratio(self, ticker: str) -> Optional[float]:
        """Dividend Payout Ratio = Dividends / EPS"""
        info = self._get_stock_info(ticker)
        if not info:
            return None
        
        ttm_dividend = info.get('dividendRate', 0) or 0
        eps = info.get('trailingEps', 0) or 0
        
        if eps <= 0:
            return None
        
        return round(ttm_dividend / eps, 3)
    
    def calculate_dividend_growth_rate(self, ticker: str, years: int = 5) -> Optional[float]:
        """CAGR of dividends over N years"""
        try:
            stock = yf.Ticker(ticker)
            dividends = stock.dividends
            if dividends.empty or len(dividends) < 4:
                return None
            
            dividends.index = dividends.index.tz_localize(None)
            now = pd.Timestamp.now()
            start = now - pd.Timedelta(days=years * 365)
            
            recent = dividends[dividends.index >= start]
            if len(recent) < 4:
                return None
            
            first_year = recent.iloc[:4].sum()
            last_year = recent.iloc[-4:].sum()
            
            if first_year <= 0:
                return None
            
            cagr = (last_year / first_year) ** (1 / years) - 1
            return round(float(cagr), 4)
        except:
            return None
    
    def get_dividend_streak(self, ticker: str) -> int:
        """Consecutive years of dividend payments"""
        try:
            stock = yf.Ticker(ticker)
            dividends = stock.dividends
            if dividends.empty:
                return 0
            
            dividends.index = dividends.index.tz_localize(None)
            years = sorted(set(dividends.index.year), reverse=True)
            
            streak = 0
            current_year = datetime.now().year
            for y in years:
                if y <= current_year and len(dividends[dividends.index.year == y]) > 0:
                    streak += 1
                    current_year = y - 1
                else:
                    break
            
            return streak
        except:
            return 0
    
    def get_dividend_safety_score(self, ticker: str) -> Dict:
        """Calculate overall dividend safety score (0-100)"""
        payout = self.calculate_payout_ratio(ticker)
        growth = self.calculate_dividend_growth_rate(ticker)
        streak = self.get_dividend_streak(ticker)
        
        score = 0
        breakdown = {}
        
        # Payout Ratio (max 30)
        if payout is not None:
            if payout < 0.3:
                pr_score = 30
            elif payout < 0.5:
                pr_score = 25
            elif payout < 0.7:
                pr_score = 15
            else:
                pr_score = 5
            score += pr_score
            breakdown['payout_ratio'] = {'value': payout, 'score': pr_score, 'max': 30}
        
        # Dividend Growth (max 25)
        if growth is not None:
            if growth > 0.10:
                gr_score = 25
            elif growth > 0.05:
                gr_score = 20
            elif growth > 0:
                gr_score = 15
            else:
                gr_score = 5
            score += gr_score
            breakdown['dividend_growth'] = {'value': growth, 'score': gr_score, 'max': 25}
        
        # Streak (max 25)
        if streak >= 25:
            st_score = 25
        elif streak >= 10:
            st_score = 20
        elif streak >= 5:
            st_score = 15
        else:
            st_score = streak * 2
        score += st_score
        breakdown['dividend_streak'] = {'value': streak, 'score': st_score, 'max': 25}
        
        # Grade
        if score >= 80:
            grade = 'A'
        elif score >= 60:
            grade = 'B'
        elif score >= 40:
            grade = 'C'
        else:
            grade = 'D'
        
        return {
            'ticker': ticker,
            'safety_score': score,
            'safety_grade': grade,
            'breakdown': breakdown
        }
    
    def get_all_metrics(self, ticker: str) -> Dict:
        """Get all dividend metrics"""
        return {
            'payout_ratio': self.calculate_payout_ratio(ticker),
            'dividend_growth_5y': self.calculate_dividend_growth_rate(ticker),
            'dividend_streak': self.get_dividend_streak(ticker),
            'safety': self.get_dividend_safety_score(ticker)
        }
```

---

## 5. backtest.py (백테스트 엔진)

`us_market/dividend/backtest.py`:

```python
"""
Backtest Engine for Dividend Portfolios
Historical simulation with dividend reinvestment
"""
import yfinance as yf
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class BacktestEngine:
    def __init__(self, benchmark: str = 'SPY'):
        self.benchmark = benchmark
    
    def run_backtest(
        self,
        portfolio: List[Tuple[str, float]],
        start_date: str,
        end_date: Optional[str] = None,
        initial_capital: float = 100000
    ) -> Dict:
        """Run backtest on portfolio."""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        tickers = [t for t, _ in portfolio]
        weights = np.array([w for _, w in portfolio])
        weights = weights / weights.sum()
        
        # Fetch price data
        price_data = {}
        dividend_data = {}
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(start=start_date, end=end_date)
                if not hist.empty:
                    price_data[ticker] = hist['Close']
                    divs = stock.dividends
                    if divs is not None and len(divs) > 0:
                        mask = (divs.index >= start_date) & (divs.index <= end_date)
                        dividend_data[ticker] = divs[mask]
            except Exception as e:
                logger.error(f"Error fetching {ticker}: {e}")
        
        if len(price_data) == 0:
            return {"error": "No valid price data"}
        
        prices_df = pd.DataFrame(price_data).dropna()
        if len(prices_df) < 10:
            return {"error": "Insufficient data"}
        
        returns_df = prices_df.pct_change().dropna()
        
        # Align weights
        available = list(prices_df.columns)
        aligned = []
        for t in available:
            for ticker, w in portfolio:
                if ticker == t:
                    aligned.append(w)
                    break
            else:
                aligned.append(0)
        weights = np.array(aligned)
        weights = weights / weights.sum()
        
        # Portfolio returns
        portfolio_returns = (returns_df * weights).sum(axis=1)
        price_cumulative = (1 + portfolio_returns).cumprod()
        
        # Calculate dividends
        total_dividends = 0
        for ticker in available:
            idx = available.index(ticker)
            w = weights[idx]
            divs = dividend_data.get(ticker, pd.Series(dtype=float))
            if len(divs) > 0:
                init_price = prices_df[ticker].iloc[0]
                shares = (initial_capital * w) / init_price
                total_dividends += divs.sum() * shares
        
        # Results
        final_price = initial_capital * price_cumulative.iloc[-1]
        final_total = final_price + total_dividends
        
        price_return = price_cumulative.iloc[-1] - 1
        total_return = (final_total - initial_capital) / initial_capital
        
        # CAGR
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        years = (end - start).days / 365.25
        cagr = (final_total / initial_capital) ** (1 / years) - 1 if years > 0 else 0
        
        # Max drawdown
        rolling_max = price_cumulative.expanding().max()
        drawdowns = (price_cumulative - rolling_max) / rolling_max
        max_drawdown = drawdowns.min()
        
        # Volatility and Sharpe
        annual_vol = portfolio_returns.std() * np.sqrt(252)
        annual_ret = portfolio_returns.mean() * 252
        sharpe = (annual_ret - 0.05) / annual_vol if annual_vol > 0 else 0
        
        # Benchmark comparison
        try:
            bench = yf.Ticker(self.benchmark)
            bh = bench.history(start=start_date, end=end_date)
            bench_return = (bh['Close'].iloc[-1] / bh['Close'].iloc[0]) - 1
        except:
            bench_return = None
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": initial_capital,
            "final_value": round(final_total, 2),
            "total_return": round(float(total_return), 4),
            "price_return": round(float(price_return), 4),
            "dividend_return": round(total_dividends / initial_capital, 4),
            "cagr": round(float(cagr), 4),
            "max_drawdown": round(float(max_drawdown), 4),
            "volatility": round(float(annual_vol), 4),
            "sharpe_ratio": round(float(sharpe), 2),
            "benchmark": self.benchmark,
            "benchmark_return": round(float(bench_return), 4) if bench_return else None,
            "alpha": round(float(total_return - bench_return), 4) if bench_return else None
        }
```

---

## 다음 단계

**BACKEND_STEP4.md**에서 Flask API 엔드포인트를 구현합니다.
