from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

import database as db


MAX_CHART_POINTS = 60

type Period = str | int | None

PERIOD_OPTIONS: list[tuple[str, int | None]] = [
    ("Mês", "month"),
    ("3M", 90),
    ("6M", 180),
    ("Tudo", None),
]

CATEGORY_COLORS: list[str] = [
    "#6C63FF",
    "#FF8C42",
    "#4FC3F7",
    "#00C896",
    "#F06292",
]


@dataclass
class DashboardState:
    selected_period: Period = "month"


@dataclass
class BalanceSummary:
    balance: float
    income: float
    expense: float


@dataclass
class CategoryRow:
    name: str
    value: float
    percentage: float
    color: str


@dataclass
class ChartPoint:
    index: int
    accumulated: float
    label: str


@dataclass
class DashboardData:
    movements: list[dict]
    balance: BalanceSummary
    top_categories: list[CategoryRow]
    chart_points: list[ChartPoint]
    latest: list[dict]


def load_dashboard_data(period: Period) -> DashboardData:
    all_movements = db.list_movements()
    all_movements_sorted = sorted(
        all_movements, key=lambda m: _parse_date(m["date"]), reverse=True
    )
    filtered = _filter_by_period(all_movements, period)

    return DashboardData(
        movements=filtered,
        balance=_compute_balance(filtered),
        top_categories=_compute_top_categories(filtered),
        chart_points=_compute_chart_points(filtered),
        latest=all_movements_sorted[:5],
    )


def _filter_by_period(movements: list[dict], period: Period) -> list[dict]:
    if period is None:
        return movements
    if period == "month":
        today = datetime.today()
        return [
            m for m in movements
            if _parse_date(m["date"]).year  == today.year
            and _parse_date(m["date"]).month == today.month
        ]

    cutoff = datetime.today() - timedelta(days=period)
    return [m for m in movements if _parse_date(m["date"]) >= cutoff]


def _parse_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        return datetime.strptime(date_str, "%Y-%m-%d")


def _compute_balance(movements: list[dict]) -> BalanceSummary:
    income  = sum(m["value"] for m in movements if m["entry_type"] == "Receita")
    expense = sum(m["value"] for m in movements if m["entry_type"] == "Despesa")
    return BalanceSummary(balance=income - expense, income=income, expense=expense)


def _compute_top_categories(movements: list[dict]) -> list[CategoryRow]:
    totals: dict[str, float] = defaultdict(float)
    for m in movements:
        if m["entry_type"] == "Despesa":
            totals[m["category"]] += m["value"]

    top = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:5]
    total_sum = sum(v for _, v in top) or 1.0

    return [
        CategoryRow(
            name=name,
            value=value,
            percentage=value / total_sum,
            color=CATEGORY_COLORS[i % len(CATEGORY_COLORS)],
        )
        for i, (name, value) in enumerate(top)
    ]


def _compute_chart_points(movements: list[dict]) -> list[ChartPoint]:
    if not movements:
        return []

    per_day: dict[str, float] = defaultdict(float)
    for m in sorted(movements, key=lambda m: _parse_date(m["date"])):
        delta = m["value"] if m["entry_type"] == "Receita" else -m["value"]
        per_day[m["date"]] += delta

    all_points: list[ChartPoint] = []
    accumulated = 0.0
    for i, (date, delta) in enumerate(sorted(per_day.items(), key=lambda x: _parse_date(x[0]))):
        accumulated += delta
        all_points.append(ChartPoint(
            index=i,
            accumulated=round(accumulated, 2),
            label=date,
        ))

    if len(all_points) <= MAX_CHART_POINTS:
        return all_points

    step = len(all_points) / MAX_CHART_POINTS
    indices = {int(i * step) for i in range(MAX_CHART_POINTS)}
    indices.add(len(all_points) - 1)
    return [all_points[i] for i in sorted(indices)]
