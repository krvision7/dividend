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
