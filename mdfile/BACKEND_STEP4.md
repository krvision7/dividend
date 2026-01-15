# Dividend System Blueprint - Backend Step 4
# Flask API 엔드포인트

## 개요
이 문서는 배당 시스템의 Flask API 엔드포인트를 구현합니다.

---

## 1. flask_app.py (배당 관련 라우트)

`flask_app.py`에 다음 라우트를 추가:

```python
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)


# ============================================
# 페이지 라우트
# ============================================

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/app')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/dividend')
def dividend_page():
    """Dividend Optimizer page"""
    return render_template('dividend.html')


# ============================================
# 배당 API 라우트
# ============================================

@app.route('/api/dividend/themes')
def get_dividend_themes():
    """Get available themes for UI"""
    try:
        from us_market.dividend.engine import DividendEngine
        engine = DividendEngine()
        return jsonify(engine.get_themes())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dividend/all-tiers', methods=['POST'])
def get_all_tier_portfolios():
    """Generate all 3 tier portfolios for a given theme"""
    try:
        data = request.json or {}
        theme_id = data.get('theme_id', 'max_monthly_income')
        target_monthly_krw = float(data.get('target_monthly_krw', 1000000))
        fx_rate = float(data.get('fx_rate', 1420))
        tax_rate = float(data.get('tax_rate', 15.4)) / 100.0
        optimize_mode = data.get('optimize_mode', 'greedy')
        
        from us_market.dividend.engine import DividendEngine
        engine = DividendEngine()
        
        results = {}
        for tier in ['defensive', 'balanced', 'aggressive']:
            result = engine.generate_portfolio(
                theme_id=theme_id,
                tier_id=tier,
                target_monthly_krw=target_monthly_krw,
                fx_rate=fx_rate,
                tax_rate=tax_rate,
                optimize_mode=optimize_mode
            )
            results[tier] = result
        return jsonify(results)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/dividend/risk-metrics/<ticker>')
def get_dividend_risk_metrics(ticker):
    """Get risk metrics for a dividend asset"""
    try:
        from us_market.dividend.risk_analytics import RiskAnalytics
        
        period = request.args.get('period', '1y')
        ra = RiskAnalytics()
        metrics = ra.get_all_risk_metrics(ticker, period)
        
        # Add risk grade
        vol = metrics.get('volatility_annual')
        dd = metrics.get('max_drawdown')
        if vol is not None and dd is not None:
            if vol < 0.15 and abs(dd) < 0.20:
                metrics['risk_grade'] = 'A'
            elif vol < 0.25 and abs(dd) < 0.35:
                metrics['risk_grade'] = 'B'
            else:
                metrics['risk_grade'] = 'C'
        else:
            metrics['risk_grade'] = 'N/A'
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dividend/sustainability/<ticker>')
def get_dividend_sustainability(ticker):
    """Get dividend sustainability analysis"""
    try:
        from us_market.dividend.dividend_analyzer import DividendAnalyzer
        da = DividendAnalyzer()
        metrics = da.get_all_metrics(ticker)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dividend/optimize-advanced', methods=['POST'])
def optimize_dividend_advanced():
    """Advanced portfolio optimization with mode selection"""
    try:
        data = request.json or {}
        theme_id = data.get('theme_id', 'max_monthly_income')
        tier_id = data.get('tier_id', 'balanced')
        target_monthly_krw = float(data.get('target_monthly_krw', 1000000))
        fx_rate = float(data.get('fx_rate', 1420))
        tax_rate = float(data.get('tax_rate', 15.4)) / 100.0
        optimize_mode = data.get('optimize_mode', 'risk_parity')
        
        from us_market.dividend.engine import DividendEngine
        engine = DividendEngine()
        
        result = engine.generate_portfolio(
            theme_id=theme_id,
            tier_id=tier_id,
            target_monthly_krw=target_monthly_krw,
            fx_rate=fx_rate,
            tax_rate=tax_rate,
            optimize_mode=optimize_mode
        )
        return jsonify(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/dividend/backtest', methods=['POST'])
def run_dividend_backtest():
    """Run backtest on a dividend portfolio"""
    try:
        from us_market.dividend.backtest import BacktestEngine
        
        data = request.json or {}
        portfolio = data.get('portfolio', [])
        start_date = data.get('start_date', '2022-01-01')
        end_date = data.get('end_date')
        initial_capital = float(data.get('initial_capital', 100000))
        
        if not portfolio:
            return jsonify({'error': 'Portfolio is required'}), 400
        
        portfolio_tuples = [(p['ticker'], p['weight']) for p in portfolio]
        
        engine = BacktestEngine()
        result = engine.run_backtest(
            portfolio=portfolio_tuples,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital
        )
        
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============================================
# 서버 실행
# ============================================

if __name__ == '__main__':
    print('🚀 Flask Server Starting on port 5001...')
    app.run(port=5001, debug=True, use_reloader=False)
```

---

## 2. API 엔드포인트 요약

| Endpoint | Method | 설명 |
|----------|--------|------|
| `/` | GET | 랜딩 페이지 |
| `/app` | GET | 대시보드 |
| `/dividend` | GET | 배당 UI 페이지 |
| `/api/dividend/themes` | GET | 테마 목록 |
| `/api/dividend/all-tiers` | POST | 3개 티어 포트폴리오 생성 |
| `/api/dividend/risk-metrics/<ticker>` | GET | 리스크 지표 |
| `/api/dividend/sustainability/<ticker>` | GET | 배당 지속성 분석 |
| `/api/dividend/optimize-advanced` | POST | 고급 최적화 |
| `/api/dividend/backtest` | POST | 백테스트 |

---

## 3. API 사용 예시

### 포트폴리오 생성
```bash
curl -X POST http://localhost:5001/api/dividend/all-tiers \
  -H "Content-Type: application/json" \
  -d '{
    "theme_id": "max_monthly_income",
    "target_monthly_krw": 1000000,
    "fx_rate": 1420,
    "tax_rate": 15.4,
    "optimize_mode": "risk_parity"
  }'
```

### 리스크 지표 조회
```bash
curl http://localhost:5001/api/dividend/risk-metrics/SCHD
```

### 응답 예시
```json
{
  "ticker": "SCHD",
  "volatility_annual": 0.161,
  "max_drawdown": -0.14,
  "sharpe_ratio": 0.05,
  "risk_grade": "B"
}
```

---

## 4. 서버 실행

```bash
python flask_app.py
```

```
🚀 Flask Server Starting on port 5001...
 * Running on http://127.0.0.1:5001
```

---

## 다음 단계

**FRONTEND_STEP1.md**에서 랜딩 페이지(`index.html`)를 구현합니다.
