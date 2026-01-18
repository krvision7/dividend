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
