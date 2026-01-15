# Dividend System Blueprint - Backend Step 1
# 프로젝트 구조 및 설정 파일

## 개요
이 문서는 배당 최적화 시스템의 기본 폴더 구조와 설정 파일을 설정합니다.

---

## 1. 폴더 구조 생성

```bash
mkdir -p us_market/dividend/{config,data,docs}
mkdir -p templates
```

최종 구조:
```
project/
├── us_market/
│   └── dividend/
│       ├── config/           # 설정 파일
│       │   ├── dividend_plans.json
│       │   └── tags.json
│       ├── data/             # 데이터 파일
│       │   ├── universe_seed.json
│       │   └── dividend_universe.json (자동 생성)
│       ├── loader.py         # 데이터 수집
│       ├── engine.py         # 포트폴리오 생성
│       ├── portfolio_optimizer.py
│       ├── risk_analytics.py
│       └── backtest.py
├── templates/
│   ├── index.html            # 랜딩 페이지
│   ├── dashboard.html        # 대시보드
│   └── dividend.html         # 배당 UI
└── flask_app.py              # Flask 서버
```

---

## 2. tags.json 생성

`us_market/dividend/config/tags.json`:

```json
{
    "core": "장기 보유 코어 성격(분산/퀄리티 중심)",
    "satellite": "코어를 보완하는 위성 성격",
    "dividend_growth": "배당 성장 성격(증가/지속성 지향)",
    "dividend_quality": "퀄리티/재무 건전성 기반 배당",
    "high_yield": "고배당/고분배 성격(변동·감액 가능성 주의)",
    "monthly_payer": "월 단위 지급/분배 패턴",
    "quarterly": "분기 지급이 일반적",
    "reit": "리츠(부동산) 성격",
    "mreits": "모기지 리츠(금리 민감/변동성 높음)",
    "bdc": "BDC(중견기업 대출/투자) 성격",
    "utilities": "유틸리티(전력/가스 등) 성격",
    "staples": "필수소비재 성격",
    "healthcare": "헬스케어 성격",
    "energy": "에너지/정유 성격",
    "midstream": "에너지 미드스트림/파이프라인/MLP",
    "financials": "금융 성격",
    "tech_div": "배당 지급 테크/반도체",
    "covered_call": "커버드콜/옵션 프리미엄 인컴",
    "preferreds": "우선주/우선주 ETF 성격",
    "bonds": "채권 ETF/금리 민감 성격",
    "treasuries": "미국 국채 중심",
    "investment_grade": "우량 회사채 중심",
    "high_yield_bonds": "하이일드 채권 중심",
    "inflation_hedge": "인플레이션 헤지(TIPS/실물자산)",
    "international_div": "미국 상장 해외 배당 노출",
    "low_vol": "저변동성 성격",
    "value": "가치(Value) 성격",
    "growth": "성장(Growth) 성격",
    "real_assets": "실물자산(리츠/인프라/자원)"
}
```

---

## 3. universe_seed.json 생성 (샘플)

`us_market/dividend/data/universe_seed.json`:

```json
[
    {"symbol": "SCHD", "type": "ETF", "tags": ["dividend_quality", "core", "quarterly"]},
    {"symbol": "VIG", "type": "ETF", "tags": ["dividend_growth", "core", "quarterly"]},
    {"symbol": "DGRO", "type": "ETF", "tags": ["dividend_growth", "core", "quarterly"]},
    {"symbol": "VYM", "type": "ETF", "tags": ["dividend_quality", "core", "quarterly"]},
    {"symbol": "HDV", "type": "ETF", "tags": ["dividend_quality", "core", "quarterly"]},
    {"symbol": "SPYD", "type": "ETF", "tags": ["high_yield", "value", "quarterly"]},
    {"symbol": "JEPI", "type": "ETF", "tags": ["covered_call", "high_yield", "monthly_payer"]},
    {"symbol": "JEPQ", "type": "ETF", "tags": ["covered_call", "high_yield", "monthly_payer"]},
    {"symbol": "QYLD", "type": "ETF", "tags": ["covered_call", "high_yield", "monthly_payer"]},
    {"symbol": "DIVO", "type": "ETF", "tags": ["covered_call", "dividend_quality", "monthly_payer"]},
    {"symbol": "VNQ", "type": "ETF", "tags": ["reit", "real_assets", "quarterly"]},
    {"symbol": "O", "type": "STOCK", "tags": ["reit", "monthly_payer", "dividend_quality"]},
    {"symbol": "VYMI", "type": "ETF", "tags": ["international_div", "high_yield", "quarterly"]},
    {"symbol": "IDV", "type": "ETF", "tags": ["international_div", "high_yield", "quarterly"]},
    {"symbol": "XLU", "type": "ETF", "tags": ["utilities", "low_vol", "quarterly"]},
    {"symbol": "PFF", "type": "ETF", "tags": ["preferreds", "high_yield", "monthly_payer"]},
    {"symbol": "AMLP", "type": "ETF", "tags": ["midstream", "high_yield", "quarterly"]},
    {"symbol": "KO", "type": "STOCK", "tags": ["staples", "dividend_quality", "dividend_growth"]},
    {"symbol": "JNJ", "type": "STOCK", "tags": ["healthcare", "dividend_quality", "dividend_growth"]},
    {"symbol": "T", "type": "STOCK", "tags": ["high_yield", "quarterly"]},
    {"symbol": "VZ", "type": "STOCK", "tags": ["high_yield", "quarterly"]}
]
```

> **참고**: 전체 214개 티커는 실제 프로젝트에서 확장해야 합니다.

---

## 4. dividend_plans.json 생성 (핵심 테마)

`us_market/dividend/config/dividend_plans.json`:

> ⚠️ **참고**: 실제 파일은 800줄(30KB)입니다. 아래는 핵심 구조 샘플입니다.
> 전체 10개 테마를 모두 구현하려면 동일한 패턴으로 확장하세요.

### 전체 10개 테마 목록

| ID | 제목 | 설명 |
|----|------|------|
| `max_monthly_income` | 월배당 최고로 받자 | 현금흐름 최우선 |
| `silver_pension` | 실버 연금형 배당 | 월 생활비를 고르게 |
| `dividend_growth` | 장기 성장배당 | 배당 성장 중시 |
| `schd_core_quality` | 퀄리티 배당 코어 | 분산/퀄리티/일관성 |
| `covered_call_premium` | 커버드콜 프리미엄 | 옵션 프리미엄 인컴 |
| `reit_real_assets` | 리츠·실물자산 | 부동산/인프라 인컴 |
| `bdc_credit_income` | BDC·크레딧 인컴 | 중소기업 대출 인컴 |
| `utilities_low_vol_income` | 저변동 인컴 | 유틸리티/디펜시브 |
| `inflation_energy_income` | 인플레이션·에너지 | 인플레 헤지 인컴 |
| `intl_diversifier` | 글로벌 배당 분산 | 해외 배당 노출 |

### 기본 구조

```json
{
    "version": "1.0",
    "tiers": [
        {"id": "defensive", "label": "방어형", "risk": "낮음"},
        {"id": "balanced", "label": "균형형", "risk": "중간"},
        {"id": "aggressive", "label": "공격형", "risk": "높음"}
    ],
    "themes": [
        {
            "id": "max_monthly_income",
            "title": "월배당 최고로 받자",
            "subtitle": "현금흐름 최우선",
            "tiers": {
                "defensive": {
                    "card_front": {
                        "headline": "현금흐름 우선(방어)",
                        "one_liner": "인컴은 챙기되, 흔들림은 낮추는 쪽",
                        "risk_label": "중간 이하"
                    },
                    "constraints": {
                        "etf_min": 0.6,
                        "single_stock_max": 0.08,
                        "max_tag_weight": {"high_yield": 0.45, "covered_call": 0.40}
                    },
                    "allowed_tags": ["covered_call", "dividend_quality", "monthly_payer", "core"],
                    "banned_tags": ["mreits"]
                },
                "balanced": {
                    "card_front": {
                        "headline": "현금흐름 우선(균형)",
                        "one_liner": "목표 달성 + 분산을 동시에",
                        "risk_label": "중간"
                    },
                    "constraints": {
                        "etf_min": 0.5,
                        "single_stock_max": 0.10,
                        "max_tag_weight": {"high_yield": 0.55, "covered_call": 0.55}
                    },
                    "allowed_tags": ["covered_call", "high_yield", "monthly_payer", "satellite"],
                    "banned_tags": []
                },
                "aggressive": {
                    "card_front": {
                        "headline": "현금흐름 극대화",
                        "one_liner": "수익률 최우선. 감액/변동 가능성 큼",
                        "risk_label": "높음"
                    },
                    "constraints": {
                        "etf_min": 0.35,
                        "single_stock_max": 0.12,
                        "max_tag_weight": {"high_yield": 0.75, "covered_call": 0.75}
                    },
                    "allowed_tags": ["high_yield", "covered_call", "reit", "bdc", "monthly_payer"],
                    "banned_tags": []
                }
            }
        },
        {
            "id": "silver_pension",
            "title": "실버 연금형 배당",
            "subtitle": "월 생활비를 '고르게' 받는 것을 최우선",
            "tiers": {
                "defensive": {
                    "card_front": {
                        "headline": "연금형(방어)",
                        "one_liner": "월별 입금 안정감을 최우선",
                        "risk_label": "낮음"
                    },
                    "constraints": {"etf_min": 0.75, "single_stock_max": 0.06},
                    "allowed_tags": ["dividend_quality", "low_vol", "core", "monthly_payer"],
                    "banned_tags": ["mreits", "high_yield_bonds"]
                },
                "balanced": {
                    "card_front": {"headline": "연금형(균형)", "one_liner": "안정 + 목표 현금흐름", "risk_label": "중간"},
                    "constraints": {"etf_min": 0.65, "single_stock_max": 0.08},
                    "allowed_tags": ["dividend_quality", "covered_call", "core"],
                    "banned_tags": ["mreits"]
                },
                "aggressive": {
                    "card_front": {"headline": "연금형(공격)", "one_liner": "현금흐름을 높이되, 월별 편차는 관리", "risk_label": "중간~높음"},
                    "constraints": {"etf_min": 0.55, "single_stock_max": 0.10},
                    "allowed_tags": ["covered_call", "high_yield", "monthly_payer", "reit", "bdc"],
                    "banned_tags": []
                }
            }
        },
        {
            "id": "dividend_growth",
            "title": "장기 성장배당",
            "subtitle": "배당 '지금'보다 '앞으로'를 중시",
            "tiers": {
                "defensive": {
                    "card_front": {"headline": "성장배당(방어)", "one_liner": "배당 성장 + 변동성 낮춤", "risk_label": "낮음"},
                    "constraints": {"etf_min": 0.70, "single_stock_max": 0.07},
                    "allowed_tags": ["dividend_growth", "dividend_quality", "core", "low_vol"],
                    "banned_tags": ["covered_call", "mreits"]
                },
                "balanced": {
                    "card_front": {"headline": "성장배당(균형)", "one_liner": "배당 성장 + 적당한 인컴", "risk_label": "중간"},
                    "constraints": {"etf_min": 0.60, "single_stock_max": 0.10},
                    "allowed_tags": ["dividend_growth", "tech_div", "dividend_quality"],
                    "banned_tags": ["mreits"]
                },
                "aggressive": {
                    "card_front": {"headline": "성장배당(공격)", "one_liner": "성장 섹터 비중↑", "risk_label": "중간~높음"},
                    "constraints": {"etf_min": 0.45, "single_stock_max": 0.12},
                    "allowed_tags": ["tech_div", "growth", "dividend_growth"],
                    "banned_tags": []
                }
            }
        }
    ]
}
```

---

## 5. Python 의존성

`requirements.txt`:

```
flask>=2.0
yfinance>=0.2.0
pandas>=1.5
numpy>=1.20
scipy>=1.9
```

설치:
```bash
pip install -r requirements.txt
```

---

## 다음 단계

**BACKEND_STEP2.md**에서 `loader.py`를 구현하여 yfinance에서 배당 데이터를 수집합니다.
