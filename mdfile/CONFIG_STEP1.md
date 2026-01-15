# Dividend System Blueprint - Config Step 1
# dividend_plans.json 테마 1-5

## 개요
이 파일은 `dividend_plans.json`의 테마 1-5를 포함합니다.

---

## dividend_plans.json (Part 1/2)

`us_market/dividend/config/dividend_plans.json`:

```json
{
    "version": "1.0",
    "tiers": [
        {"id": "defensive", "label": "방어형", "risk": "낮음"},
        {"id": "balanced", "label": "균형형", "risk": "중간"},
        {"id": "aggressive", "label": "공격형", "risk": "높음"}
    ],
    "objectives": {
        "a_target_match": "목표 월 현금흐름 오차 최소화",
        "b_volatility_min": "가격 변동성 최소화",
        "c_cashflow_smooth": "월별 현금흐름 들쭉날쭉 최소화"
    },
    "themes": [
        {
            "id": "max_monthly_income",
            "title": "월배당 최고로 받자",
            "subtitle": "현금흐름 최우선. 대신 변동·감액 가능성을 명확히 안내",
            "default_objective": "a_target_match",
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
                        "sector_cap": 0.25,
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
                        "sector_cap": 0.30,
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
                        "sector_cap": 0.35,
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
            "default_objective": "c_cashflow_smooth",
            "tiers": {
                "defensive": {
                    "card_front": {
                        "headline": "연금형(방어)",
                        "one_liner": "월별 입금 안정감을 최우선",
                        "risk_label": "낮음"
                    },
                    "constraints": {
                        "etf_min": 0.75,
                        "single_stock_max": 0.06,
                        "sector_cap": 0.22,
                        "max_tag_weight": {"high_yield": 0.35, "covered_call": 0.35}
                    },
                    "allowed_tags": ["dividend_quality", "low_vol", "core", "monthly_payer"],
                    "banned_tags": ["mreits", "high_yield_bonds"]
                },
                "balanced": {
                    "card_front": {
                        "headline": "연금형(균형)",
                        "one_liner": "안정 + 목표 현금흐름",
                        "risk_label": "중간"
                    },
                    "constraints": {
                        "etf_min": 0.65,
                        "single_stock_max": 0.08,
                        "sector_cap": 0.25,
                        "max_tag_weight": {"high_yield": 0.45, "covered_call": 0.45}
                    },
                    "allowed_tags": ["dividend_quality", "covered_call", "core"],
                    "banned_tags": ["mreits"]
                },
                "aggressive": {
                    "card_front": {
                        "headline": "연금형(공격)",
                        "one_liner": "현금흐름을 높이되, 월별 편차는 관리",
                        "risk_label": "중간~높음"
                    },
                    "constraints": {
                        "etf_min": 0.55,
                        "single_stock_max": 0.10,
                        "sector_cap": 0.30,
                        "max_tag_weight": {"high_yield": 0.60, "covered_call": 0.60}
                    },
                    "allowed_tags": ["covered_call", "high_yield", "monthly_payer", "reit", "bdc"],
                    "banned_tags": []
                }
            }
        },
        {
            "id": "dividend_growth",
            "title": "장기 성장배당",
            "subtitle": "배당 '지금'보다 '앞으로'를 중시(성장+배당 증가)",
            "default_objective": "b_volatility_min",
            "tiers": {
                "defensive": {
                    "card_front": {
                        "headline": "성장배당(방어)",
                        "one_liner": "배당 성장 + 변동성 낮춤",
                        "risk_label": "낮음"
                    },
                    "constraints": {
                        "etf_min": 0.70,
                        "single_stock_max": 0.07,
                        "sector_cap": 0.25,
                        "max_tag_weight": {"high_yield": 0.25}
                    },
                    "allowed_tags": ["dividend_growth", "dividend_quality", "core", "low_vol"],
                    "banned_tags": ["covered_call", "mreits"]
                },
                "balanced": {
                    "card_front": {
                        "headline": "성장배당(균형)",
                        "one_liner": "배당 성장 + 적당한 인컴",
                        "risk_label": "중간"
                    },
                    "constraints": {
                        "etf_min": 0.60,
                        "single_stock_max": 0.10,
                        "sector_cap": 0.30,
                        "max_tag_weight": {"high_yield": 0.35}
                    },
                    "allowed_tags": ["dividend_growth", "tech_div", "dividend_quality"],
                    "banned_tags": ["mreits"]
                },
                "aggressive": {
                    "card_front": {
                        "headline": "성장배당(공격)",
                        "one_liner": "성장 섹터 비중↑, 배당은 보조",
                        "risk_label": "중간~높음"
                    },
                    "constraints": {
                        "etf_min": 0.45,
                        "single_stock_max": 0.12,
                        "sector_cap": 0.35,
                        "max_tag_weight": {"high_yield": 0.45}
                    },
                    "allowed_tags": ["tech_div", "growth", "dividend_growth"],
                    "banned_tags": []
                }
            }
        },
        {
            "id": "schd_core_quality",
            "title": "퀄리티 배당 코어",
            "subtitle": "'대표 배당 코어' 스타일(분산/퀄리티/일관성)",
            "default_objective": "b_volatility_min",
            "tiers": {
                "defensive": {
                    "card_front": {
                        "headline": "코어(방어)",
                        "one_liner": "분산·퀄리티 중심 코어",
                        "risk_label": "낮음"
                    },
                    "constraints": {
                        "etf_min": 0.80,
                        "single_stock_max": 0.06,
                        "sector_cap": 0.22,
                        "max_tag_weight": {"high_yield": 0.25}
                    },
                    "allowed_tags": ["dividend_quality", "core", "value", "low_vol"],
                    "banned_tags": ["covered_call", "mreits"]
                },
                "balanced": {
                    "card_front": {
                        "headline": "코어(균형)",
                        "one_liner": "코어 + 위성 소량",
                        "risk_label": "중간"
                    },
                    "constraints": {
                        "etf_min": 0.70,
                        "single_stock_max": 0.08,
                        "sector_cap": 0.25,
                        "max_tag_weight": {"high_yield": 0.35}
                    },
                    "allowed_tags": ["dividend_quality", "core", "satellite"],
                    "banned_tags": ["mreits"]
                },
                "aggressive": {
                    "card_front": {
                        "headline": "코어(공격)",
                        "one_liner": "코어 유지 + 인컴 강화",
                        "risk_label": "중간"
                    },
                    "constraints": {
                        "etf_min": 0.60,
                        "single_stock_max": 0.10,
                        "sector_cap": 0.30,
                        "max_tag_weight": {"high_yield": 0.45, "covered_call": 0.35}
                    },
                    "allowed_tags": ["dividend_quality", "high_yield", "satellite"],
                    "banned_tags": []
                }
            }
        },
        {
            "id": "covered_call_premium",
            "title": "커버드콜 프리미엄 인컴",
            "subtitle": "옵션 프리미엄 기반 인컴을 테마로 묶음",
            "default_objective": "a_target_match",
            "tiers": {
                "defensive": {
                    "card_front": {
                        "headline": "프리미엄 인컴(방어)",
                        "one_liner": "커버드콜 비중을 제한해 방어",
                        "risk_label": "중간"
                    },
                    "constraints": {
                        "etf_min": 0.70,
                        "single_stock_max": 0.08,
                        "sector_cap": 0.25,
                        "max_tag_weight": {"covered_call": 0.50}
                    },
                    "allowed_tags": ["covered_call", "dividend_quality", "core"],
                    "banned_tags": ["mreits"]
                },
                "balanced": {
                    "card_front": {
                        "headline": "프리미엄 인컴(균형)",
                        "one_liner": "커버드콜을 인컴 축으로 활용",
                        "risk_label": "중간"
                    },
                    "constraints": {
                        "etf_min": 0.60,
                        "single_stock_max": 0.10,
                        "sector_cap": 0.30,
                        "max_tag_weight": {"covered_call": 0.70}
                    },
                    "allowed_tags": ["covered_call", "high_yield", "monthly_payer"],
                    "banned_tags": []
                },
                "aggressive": {
                    "card_front": {
                        "headline": "프리미엄 인컴(공격)",
                        "one_liner": "인컴 최대. 상승장 수익 제한 가능",
                        "risk_label": "높음"
                    },
                    "constraints": {
                        "etf_min": 0.45,
                        "single_stock_max": 0.12,
                        "sector_cap": 0.35,
                        "max_tag_weight": {"covered_call": 0.85}
                    },
                    "allowed_tags": ["covered_call", "high_yield"],
                    "banned_tags": []
                }
            }
        }
    ]
}
```

> **참고**: 이 파일은 테마 1-5만 포함합니다. 테마 6-10은 `CONFIG_STEP2.md`를 참조하세요.

---

## 다음 단계

**CONFIG_STEP2.md**에서 나머지 테마 6-10을 추가합니다.
