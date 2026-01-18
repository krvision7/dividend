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

    def get_themes(self) -> List[Dict]:
        """Get list of available themes for UI"""
        themes = []
        for t in self.plans.get('themes', []):
            themes.append({
                'id': t['id'],
                'title': t['title'],
                'subtitle': t['subtitle']
            })
        return themes

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
