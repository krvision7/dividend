# Dividend System Blueprint - Config Step 2
# dividend_plans.json 테마 6-10

## 개요
이 파일은 `dividend_plans.json`의 테마 6-10을 포함합니다.

---

## dividend_plans.json (Part 2/2)

`us_market/dividend/config/dividend_plans.json`의 themes 배열에 추가:

```json
        {
            "id": "reit_real_assets",
            "title": "리츠·실물자산 인컴",
            "subtitle": "부동산/인프라/실물자산 성격으로 인컴 강화",
            "default_objective": "c_cashflow_smooth",
            "tiers": {
                "defensive": {
                    "card_front": {
                        "headline": "실물자산(방어)",
                        "one_liner": "대형/퀄리티 리츠 중심",
                        "risk_label": "중간"
                    },
                    "constraints": {
                        "etf_min": 0.65,
                        "single_stock_max": 0.08,
                        "sector_cap": 0.35,
                        "max_tag_weight": {"reit": 0.60}
                    },
                    "allowed_tags": ["reit", "real_assets", "dividend_quality"],
                    "banned_tags": ["mreits"]
                },
                "balanced": {
                    "card_front": {
                        "headline": "실물자산(균형)",
                        "one_liner": "리츠 + 인프라/유틸리티 혼합",
                        "risk_label": "중간"
                    },
                    "constraints": {
                        "etf_min": 0.55,
                        "single_stock_max": 0.10,
                        "sector_cap": 0.40,
                        "max_tag_weight": {"reit": 0.70}
                    },
                    "allowed_tags": ["reit", "utilities", "real_assets"],
                    "banned_tags": ["mreits"]
                },
                "aggressive": {
                    "card_front": {
                        "headline": "실물자산(공격)",
                        "one_liner": "고수익 자산 비중↑ (변동 주의)",
                        "risk_label": "높음"
                    },
                    "constraints": {
                        "etf_min": 0.45,
                        "single_stock_max": 0.12,
                        "sector_cap": 0.45,
                        "max_tag_weight": {"reit": 0.80, "high_yield": 0.65}
                    },
                    "allowed_tags": ["reit", "bdc", "high_yield"],
                    "banned_tags": []
                }
            }
        },
        {
            "id": "bdc_credit_income",
            "title": "BDC·크레딧 인컴",
            "subtitle": "대출/크레딧 기반 인컴(현금흐름은 강하나 리스크 이해 필요)",
            "default_objective": "a_target_match",
            "tiers": {
                "defensive": {
                    "card_front": {
                        "headline": "크레딧 인컴(방어)",
                        "one_liner": "크레딧 비중을 제한해 분산",
                        "risk_label": "중간"
                    },
                    "constraints": {
                        "etf_min": 0.65,
                        "single_stock_max": 0.08,
                        "sector_cap": 0.35,
                        "max_tag_weight": {"bdc": 0.35, "high_yield_bonds": 0.35}
                    },
                    "allowed_tags": ["bdc", "investment_grade", "dividend_quality"],
                    "banned_tags": ["mreits"]
                },
                "balanced": {
                    "card_front": {
                        "headline": "크레딧 인컴(균형)",
                        "one_liner": "BDC + 하이일드 일부",
                        "risk_label": "중간~높음"
                    },
                    "constraints": {
                        "etf_min": 0.55,
                        "single_stock_max": 0.10,
                        "sector_cap": 0.40,
                        "max_tag_weight": {"bdc": 0.55, "high_yield_bonds": 0.55}
                    },
                    "allowed_tags": ["bdc", "high_yield_bonds", "high_yield", "monthly_payer"],
                    "banned_tags": []
                },
                "aggressive": {
                    "card_front": {
                        "headline": "크레딧 인컴(공격)",
                        "one_liner": "인컴 극대화(경기/스프레드 민감)",
                        "risk_label": "높음"
                    },
                    "constraints": {
                        "etf_min": 0.45,
                        "single_stock_max": 0.12,
                        "sector_cap": 0.45,
                        "max_tag_weight": {"bdc": 0.75, "high_yield_bonds": 0.75}
                    },
                    "allowed_tags": ["bdc", "high_yield_bonds", "high_yield"],
                    "banned_tags": []
                }
            }
        },
        {
            "id": "utilities_low_vol_income",
            "title": "저변동 인컴(유틸리티·디펜시브)",
            "subtitle": "변동성을 낮추면서 배당을 받는 디펜시브 성격",
            "default_objective": "b_volatility_min",
            "tiers": {
                "defensive": {
                    "card_front": {
                        "headline": "저변동(방어)",
                        "one_liner": "변동성 최소화 우선",
                        "risk_label": "낮음"
                    },
                    "constraints": {
                        "etf_min": 0.80,
                        "single_stock_max": 0.06,
                        "sector_cap": 0.30,
                        "max_tag_weight": {"utilities": 0.40}
                    },
                    "allowed_tags": ["utilities", "staples", "healthcare", "low_vol", "dividend_quality"],
                    "banned_tags": ["covered_call", "mreits", "high_yield"]
                },
                "balanced": {
                    "card_front": {
                        "headline": "저변동(균형)",
                        "one_liner": "디펜시브 + 코어 배당 혼합",
                        "risk_label": "낮음~중간"
                    },
                    "constraints": {
                        "etf_min": 0.70,
                        "single_stock_max": 0.08,
                        "sector_cap": 0.33,
                        "max_tag_weight": {"utilities": 0.45}
                    },
                    "allowed_tags": ["utilities", "dividend_quality", "core", "value"],
                    "banned_tags": ["mreits"]
                },
                "aggressive": {
                    "card_front": {
                        "headline": "저변동(공격)",
                        "one_liner": "디펜시브 기반으로 인컴 조금 더",
                        "risk_label": "중간"
                    },
                    "constraints": {
                        "etf_min": 0.60,
                        "single_stock_max": 0.10,
                        "sector_cap": 0.35,
                        "max_tag_weight": {"high_yield": 0.40}
                    },
                    "allowed_tags": ["utilities", "high_yield", "satellite"],
                    "banned_tags": []
                }
            }
        },
        {
            "id": "inflation_energy_income",
            "title": "인플레이션·에너지 인컴",
            "subtitle": "에너지/자원/인플레이션 헤지 성격을 인컴과 결합",
            "default_objective": "a_target_match",
            "tiers": {
                "defensive": {
                    "card_front": {
                        "headline": "인플레·에너지(방어)",
                        "one_liner": "헤지 성격은 보조, 과도한 쏠림 방지",
                        "risk_label": "중간"
                    },
                    "constraints": {
                        "etf_min": 0.65,
                        "single_stock_max": 0.08,
                        "sector_cap": 0.35,
                        "max_tag_weight": {"energy": 0.40, "midstream": 0.35}
                    },
                    "allowed_tags": ["energy", "inflation_hedge", "dividend_quality"],
                    "banned_tags": ["mreits"]
                },
                "balanced": {
                    "card_front": {
                        "headline": "인플레·에너지(균형)",
                        "one_liner": "배당 + 헤지 + 분산",
                        "risk_label": "중간"
                    },
                    "constraints": {
                        "etf_min": 0.55,
                        "single_stock_max": 0.10,
                        "sector_cap": 0.40,
                        "max_tag_weight": {"energy": 0.55, "midstream": 0.45}
                    },
                    "allowed_tags": ["energy", "midstream", "high_yield", "real_assets"],
                    "banned_tags": []
                },
                "aggressive": {
                    "card_front": {
                        "headline": "인플레·에너지(공격)",
                        "one_liner": "인컴 극대화(가격/정책 민감)",
                        "risk_label": "높음"
                    },
                    "constraints": {
                        "etf_min": 0.45,
                        "single_stock_max": 0.12,
                        "sector_cap": 0.45,
                        "max_tag_weight": {"energy": 0.70, "midstream": 0.65}
                    },
                    "allowed_tags": ["energy", "midstream", "high_yield"],
                    "banned_tags": []
                }
            }
        },
        {
            "id": "intl_diversifier",
            "title": "글로벌 배당 분산",
            "subtitle": "미국 상장 ETF로 해외 배당 노출을 섞어 분산",
            "default_objective": "b_volatility_min",
            "tiers": {
                "defensive": {
                    "card_front": {
                        "headline": "글로벌(방어)",
                        "one_liner": "분산 목적. 해외 비중은 제한적으로",
                        "risk_label": "중간"
                    },
                    "constraints": {
                        "etf_min": 0.75,
                        "single_stock_max": 0.07,
                        "sector_cap": 0.30,
                        "max_tag_weight": {"international_div": 0.35}
                    },
                    "allowed_tags": ["international_div", "dividend_quality", "core"],
                    "banned_tags": ["mreits"]
                },
                "balanced": {
                    "card_front": {
                        "headline": "글로벌(균형)",
                        "one_liner": "미국 코어 + 해외 배당 보완",
                        "risk_label": "중간"
                    },
                    "constraints": {
                        "etf_min": 0.65,
                        "single_stock_max": 0.09,
                        "sector_cap": 0.35,
                        "max_tag_weight": {"international_div": 0.50}
                    },
                    "allowed_tags": ["international_div", "value", "dividend_quality"],
                    "banned_tags": []
                },
                "aggressive": {
                    "card_front": {
                        "headline": "글로벌(공격)",
                        "one_liner": "해외 인컴 비중↑(환율 변동 주의)",
                        "risk_label": "중간~높음"
                    },
                    "constraints": {
                        "etf_min": 0.55,
                        "single_stock_max": 0.10,
                        "sector_cap": 0.40,
                        "max_tag_weight": {"international_div": 0.65, "high_yield": 0.55}
                    },
                    "allowed_tags": ["international_div", "high_yield", "real_assets"],
                    "banned_tags": []
                }
            }
        }
```

---

## 전체 테마 목록

| # | ID | 제목 | 위치 |
|---|-----|------|------|
| 1 | `max_monthly_income` | 월배당 최고로 받자 | CONFIG_STEP1 |
| 2 | `silver_pension` | 실버 연금형 배당 | CONFIG_STEP1 |
| 3 | `dividend_growth` | 장기 성장배당 | CONFIG_STEP1 |
| 4 | `schd_core_quality` | 퀄리티 배당 코어 | CONFIG_STEP1 |
| 5 | `covered_call_premium` | 커버드콜 프리미엄 인컴 | CONFIG_STEP1 |
| 6 | `reit_real_assets` | 리츠·실물자산 인컴 | CONFIG_STEP2 (현재) |
| 7 | `bdc_credit_income` | BDC·크레딧 인컴 | CONFIG_STEP2 (현재) |
| 8 | `utilities_low_vol_income` | 저변동 인컴 | CONFIG_STEP2 (현재) |
| 9 | `inflation_energy_income` | 인플레이션·에너지 인컴 | CONFIG_STEP2 (현재) |
| 10 | `intl_diversifier` | 글로벌 배당 분산 | CONFIG_STEP2 (현재) |

---

## 다음 단계

**DATA_STEP1.md**에서 `universe_seed.json` 전체 티커 목록을 추가합니다.
