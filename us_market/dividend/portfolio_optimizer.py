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
