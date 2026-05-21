from __future__ import annotations

import math
from typing import Any


BASE_SCORE_MAX = 2.0


def score_banker(value: float) -> float:
    breakpoints = [(0, 0.0), (3, 0.2), (8, 0.4), (12, 0.6), (16, 0.8), (20, 1.0)]
    if value <= 0:
        return 0.0
    if value >= 20:
        return 1.0
    for i in range(len(breakpoints) - 1):
        x0, y0 = breakpoints[i]
        x1, y1 = breakpoints[i + 1]
        if x0 <= value <= x1:
            return round(y0 + (y1 - y0) * (value - x0) / (x1 - x0), 4)
    return 0.0


def quadrant_name(value: int) -> str:
    return {
        1: "T\u0102NG GI\u00c1",
        2: "SUY Y\u1ebeU",
        3: "GI\u1ea2M GI\u00c1",
        4: "T\u00cdCH L\u0168Y",
    }.get(value, "GI\u1ea2M GI\u00c1")


def score_rrg(value: int) -> float:
    return {1: 1.0, 4: 0.75, 2: 0.5, 3: 0.25}.get(value, 0.25)


def safe_score(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(parsed) or math.isinf(parsed):
        return default
    return parsed


def build_score_payload(
    *,
    mcdx_score: float,
    rrg_score: float,
    extra_components: dict[str, float] | None = None,
) -> dict[str, Any]:
    components = {
        "mcdx_score": round(safe_score(mcdx_score), 4),
        "rrg_score": round(safe_score(rrg_score), 4),
    }

    for key, value in (extra_components or {}).items():
        if not key.endswith("_score"):
            key = f"{key}_score"
        components[key] = round(safe_score(value), 4)

    total_score = round(sum(components.values()), 2)
    score_max = BASE_SCORE_MAX + sum(
        1.0 for key in components if key not in {"mcdx_score", "rrg_score"}
    )
    extra_score = round(sum(
        value for key, value in components.items() if key not in {"mcdx_score", "rrg_score"}
    ), 4)

    return {
        "total_score": total_score,
        "mcdx_score": components["mcdx_score"],
        "rrg_score": components["rrg_score"],
        "extra_score": extra_score,
        "score_max": score_max,
        "score_components": components,
    }


def build_base_score_from_raw(banker_value: float, quadrant: int) -> dict[str, Any]:
    return build_score_payload(
        mcdx_score=score_banker(banker_value),
        rrg_score=score_rrg(quadrant),
    )
