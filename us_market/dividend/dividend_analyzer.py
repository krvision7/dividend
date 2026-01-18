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
