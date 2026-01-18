# 🎯 Dividend System Blueprint

> 이 Blueprint를 순서대로 LLM에 주입하면 배당 최적화 시스템이 재현됩니다.

---

## 📋 사용 방법

```
1. 빈 프로젝트 폴더 생성
2. 아래 순서대로 각 파일을 LLM에 주입하여 코드 생성

[Phase 1: 설정]
BACKEND_STEP1.md → 폴더 구조 + tags.json
CONFIG_STEP1.md  → dividend_plans.json 테마 1-5
CONFIG_STEP2.md  → dividend_plans.json 테마 6-10
DATA_STEP1.md    → universe_seed.json ETF 88개
DATA_STEP2.md    → universe_seed.json 개별주 126개

[Phase 2: 백엔드]
BACKEND_STEP2.md → loader.py
BACKEND_STEP3.md → engine + optimizer + analyzer + backtest
BACKEND_STEP4.md → Flask API

[Phase 3: 프론트엔드]
FRONTEND_STEP1.md → 랜딩 페이지
FRONTEND_STEP2.md → 대시보드
FRONTEND_STEP3.md → 배당 UI HTML/CSS
FRONTEND_STEP4.md → 배당 UI JavaScript

3. python flask_app.py → 서버 실행
```

---

## 📁 Blueprint 파일 구조

| 단계 | 파일 | 크기 | 설명 |
|------|------|------|------|
| **설정** | | | |
| 1A | BACKEND_STEP1.md | 11KB | 폴더 구조, tags.json |
| 1B | CONFIG_STEP1.md | 11KB | dividend_plans.json 테마 1-5 |
| 1C | CONFIG_STEP2.md | 11KB | dividend_plans.json 테마 6-10 |
| 1D | DATA_STEP1.md | 7KB | universe_seed.json ETF 88개 |
| 1E | DATA_STEP2.md | 9KB | universe_seed.json 개별주 126개 |
| **백엔드** | | | |
| 2 | BACKEND_STEP2.md | 7KB | loader.py |
| 3 | BACKEND_STEP3.md | 27KB | engine.py, optimizer, analytics, backtest |
| 4 | BACKEND_STEP4.md | 8KB | Flask API |
| **프론트엔드** | | | |
| 5 | FRONTEND_STEP1.md | 7KB | index.html 랜딩 |
| 6 | FRONTEND_STEP2.md | 8KB | dashboard.html |
| 7 | FRONTEND_STEP3.md | 13KB | dividend.html HTML/CSS |
| 8 | FRONTEND_STEP4.md | 14KB | dividend.html JavaScript |

**총합: 13개 파일 / ~133KB**

---

## 📊 포함되는 전체 데이터

### 투자 테마 (10개)
| # | ID | 제목 |
|---|----|------|
| 1 | max_monthly_income | 월배당 최고로 받자 |
| 2 | silver_pension | 실버 연금형 배당 |
| 3 | dividend_growth | 장기 성장배당 |
| 4 | schd_core_quality | 퀄리티 배당 코어 |
| 5 | covered_call_premium | 커버드콜 프리미엄 인컴 |
| 6 | reit_real_assets | 리츠·실물자산 인컴 |
| 7 | bdc_credit_income | BDC·크레딧 인컴 |
| 8 | utilities_low_vol_income | 저변동 인컴 |
| 9 | inflation_energy_income | 인플레이션·에너지 인컴 |
| 10 | intl_diversifier | 글로벌 배당 분산 |

### 유니버스 (214개 티커)
- **ETF**: 88개 (SCHD, JEPI, VNQ, VIG 등)
- **개별주**: 126개 (KO, JNJ, MSFT, O 등)

---

## 🛠️ 생성되는 프로젝트 구조

```
project/
├── us_market/
│   └── dividend/
│       ├── config/
│       │   ├── dividend_plans.json    # 10개 테마, 3개 티어
│       │   └── tags.json              # 28개 태그
│       ├── data/
│       │   ├── universe_seed.json     # 214개 티커
│       │   └── dividend_universe.json # 자동 생성
│       ├── loader.py
│       ├── engine.py
│       ├── portfolio_optimizer.py
│       ├── risk_analytics.py
│       ├── dividend_analyzer.py
│       └── backtest.py
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   └── dividend.html
├── flask_app.py
└── requirements.txt
```

---

## 🔌 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/` | 랜딩 페이지 |
| GET | `/app` | 대시보드 |
| GET | `/dividend` | 배당 UI |
| GET | `/api/dividend/themes` | 테마 목록 |
| POST | `/api/dividend/all-tiers` | 3개 티어 포트폴리오 |
| GET | `/api/dividend/risk-metrics/<ticker>` | 리스크 지표 |
| GET | `/api/dividend/sustainability/<ticker>` | 배당 지속성 |
| POST | `/api/dividend/backtest` | 백테스트 |

---

## 🚀 빠른 시작

```bash
# 1. 의존성 설치
pip install flask yfinance pandas numpy scipy

# 2. 배당 데이터 수집
python us_market/dividend/loader.py

# 3. 서버 실행
python flask_app.py

# 4. 브라우저
http://localhost:5001
```

---

*Last Updated: 2025-12-20*
