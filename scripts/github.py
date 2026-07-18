from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import calendar
import json
import re
from typing import Any

import requests
from bs4 import BeautifulSoup


CONTRIBUTIONS_URL = "https://github.com/users/{username}/contributions"
LEVEL_COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}


@dataclass(frozen=True)
class ContributionDay:
    date: date
    count: int
    level: int
    color: str


@dataclass(frozen=True)
class ContributionStats:
    total_contributions: int
    average_per_day: float
    current_streak: int
    longest_streak: int
    most_active_weekday: str
    monthly_contributions: dict[str, int]


@dataclass(frozen=True)
class ContributionCalendar:
    username: str
    fetched_at: datetime
    days: list[ContributionDay]
    source: str


def fetch_contribution_markup(username: str, timeout: float = 20.0) -> str:
    if not re.fullmatch(r"[A-Za-z0-9-]+", username):
        raise ValueError("GitHub username may only contain letters, numbers, and hyphens")

    url = CONTRIBUTIONS_URL.format(username=username)
    response = requests.get(
        url,
        timeout=timeout,
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": f"github-profile-engine/1.0 (+https://github.com/{username})",
        },
    )
    response.raise_for_status()
    if not response.text.strip():
        raise ValueError(f"GitHub returned an empty contribution graph for {username}")
    return response.text


def _parse_count(element: Any, tooltip_text: str = "") -> int:
    explicit = (
        element.get("data-count")
        or element.get("data-contribution-count")
        or element.get("data-count-text")
    )
    if explicit is not None:
        match = re.search(r"\d[\d,]*", explicit)
        if match:
            return int(match.group(0).replace(",", ""))

    label = (
        element.get("aria-label")
        or element.get("data-tooltip")
        or element.get("title")
        or tooltip_text
        or ""
    )
    if re.search(r"\bno contributions?\b", label, re.IGNORECASE):
        return 0

    match = re.search(r"(\d[\d,]*)\s+contributions?", label, re.IGNORECASE)
    if match:
        return int(match.group(1).replace(",", ""))

    return 0


def _parse_level(element: Any, count: int, max_count: int | None = None) -> int:
    value = element.get("data-level")
    parsed_level: int | None = None
    if value is not None:
        try:
            parsed_level = max(0, min(4, int(value)))
        except ValueError:
            parsed_level = None

    if parsed_level is not None:
        return parsed_level

    if count <= 0:
        return 0
    if not max_count:
        return 1
    return max(1, min(4, round((count / max_count) * 4)))


def _parse_color(element: Any, level: int) -> str:
    fill = element.get("fill")
    if fill and fill.lower() not in {"none", "transparent"} and not fill.startswith("var("):
        return fill

    style = element.get("style") or ""
    match = re.search(r"(?:background-color|fill)\s*:\s*([^;]+)", style)
    if match:
        return match.group(1).strip()

    return LEVEL_COLORS.get(level, LEVEL_COLORS[0])


def _normalize_calendar_days(days: list[ContributionDay]) -> list[ContributionDay]:
    if not days:
        return []

    by_date = {day.date: day for day in days}
    current = min(by_date)
    end = max(by_date)
    normalized: list[ContributionDay] = []

    while current <= end:
        normalized.append(
            by_date.get(
                current,
                ContributionDay(
                    date=current,
                    count=0,
                    level=0,
                    color=LEVEL_COLORS[0],
                ),
            )
        )
        current += timedelta(days=1)

    return normalized


def parse_contributions(username: str, markup: str) -> ContributionCalendar:
    soup = BeautifulSoup(markup, "html.parser")
    elements = soup.select("[data-date]")
    tooltip_by_target = {
        tooltip.get("for"): tooltip.get_text(" ", strip=True)
        for tooltip in soup.select("tool-tip[for]")
        if tooltip.get("for")
    }
    parsed: dict[date, tuple[int, int | None, str | None]] = {}

    for element in elements:
        raw_date = element.get("data-date")
        if not raw_date:
            continue

        try:
            contribution_date = date.fromisoformat(raw_date)
        except ValueError:
            continue

        count = _parse_count(element, tooltip_by_target.get(element.get("id"), ""))
        raw_level = element.get("data-level")
        level = None
        if raw_level is not None:
            try:
                level = max(0, min(4, int(raw_level)))
            except ValueError:
                level = None

        color = element.get("fill")
        parsed[contribution_date] = (count, level, color)

    if not parsed:
        raise ValueError("No contribution days were found in GitHub contribution markup")

    max_count = max(count for count, _, _ in parsed.values())
    days = [
        _build_day(day, count, level, color, max_count)
        for day, (count, level, color) in sorted(parsed.items())
    ]

    return ContributionCalendar(
        username=username,
        fetched_at=datetime.now(timezone.utc),
        days=_normalize_calendar_days(days),
        source=CONTRIBUTIONS_URL.format(username=username),
    )


class _NullElement:
    def get(self, _key: str) -> None:
        return None


def _build_day(
    contribution_date: date,
    count: int,
    level: int | None,
    color: str | None,
    max_count: int,
) -> ContributionDay:
    resolved_level = level if level is not None else _parse_level(_NullElement(), count, max_count)
    fallback_color = LEVEL_COLORS.get(resolved_level, LEVEL_COLORS[0])
    resolved_color = color or fallback_color

    if resolved_color.startswith("var(") or resolved_color == "#ebedf0":
        resolved_color = fallback_color

    return ContributionDay(
        date=contribution_date,
        count=count,
        level=resolved_level,
        color=resolved_color,
    )


def fetch_contributions(username: str, timeout: float = 20.0) -> ContributionCalendar:
    markup = fetch_contribution_markup(username, timeout=timeout)
    return parse_contributions(username, markup)


def empty_calendar(
    username: str,
    days: int = 371,
    end_date: date | None = None,
) -> ContributionCalendar:
    end = end_date or date.today()
    start = end - timedelta(days=days - 1)
    generated_days = [
        ContributionDay(
            date=start + timedelta(days=offset),
            count=0,
            level=0,
            color=LEVEL_COLORS[0],
        )
        for offset in range(days)
    ]
    return ContributionCalendar(
        username=username,
        fetched_at=datetime.now(timezone.utc),
        days=generated_days,
        source="offline-empty-calendar",
    )


def compute_stats(days: list[ContributionDay]) -> ContributionStats:
    normalized = _normalize_calendar_days(sorted(days, key=lambda item: item.date))
    if not normalized:
        return ContributionStats(
            total_contributions=0,
            average_per_day=0.0,
            current_streak=0,
            longest_streak=0,
            most_active_weekday="N/A",
            monthly_contributions={},
        )

    total = sum(day.count for day in normalized)
    average = total / len(normalized)
    by_date = {day.date: day.count for day in normalized}
    current_streak = 0
    cursor = max(by_date)

    while cursor in by_date and by_date[cursor] > 0:
        current_streak += 1
        cursor -= timedelta(days=1)

    longest_streak = 0
    active_streak = 0
    weekday_totals: dict[int, int] = defaultdict(int)
    monthly: dict[str, int] = defaultdict(int)

    for day in normalized:
        if day.count > 0:
            active_streak += 1
        else:
            longest_streak = max(longest_streak, active_streak)
            active_streak = 0

        weekday_totals[day.date.weekday()] += day.count
        monthly[day.date.strftime("%Y-%m")] += day.count

    longest_streak = max(longest_streak, active_streak)
    most_active_weekday_index = max(
        range(7),
        key=lambda weekday: (weekday_totals.get(weekday, 0), -weekday),
    )

    return ContributionStats(
        total_contributions=total,
        average_per_day=round(average, 2),
        current_streak=current_streak,
        longest_streak=longest_streak,
        most_active_weekday=calendar.day_name[most_active_weekday_index],
        monthly_contributions=dict(sorted(monthly.items())),
    )


def calendar_to_dict(calendar_data: ContributionCalendar) -> dict[str, Any]:
    stats = compute_stats(calendar_data.days)
    return {
        "username": calendar_data.username,
        "fetched_at": calendar_data.fetched_at.isoformat(),
        "source": calendar_data.source,
        "stats": asdict(stats),
        "days": [
            {
                "date": day.date.isoformat(),
                "count": day.count,
                "level": day.level,
                "color": day.color,
            }
            for day in sorted(calendar_data.days, key=lambda item: item.date)
        ],
    }


def calendar_from_dict(data: dict[str, Any]) -> ContributionCalendar:
    return ContributionCalendar(
        username=str(data["username"]),
        fetched_at=datetime.fromisoformat(str(data["fetched_at"])),
        source=str(data.get("source", "unknown")),
        days=[
            ContributionDay(
                date=date.fromisoformat(str(item["date"])),
                count=int(item.get("count", 0)),
                level=max(0, min(4, int(item.get("level", 0)))),
                color=str(item.get("color") or LEVEL_COLORS[0]),
            )
            for item in data.get("days", [])
        ],
    )


def save_contributions(calendar_data: ContributionCalendar, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(calendar_to_dict(calendar_data), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_contributions(path: Path) -> ContributionCalendar:
    return calendar_from_dict(json.loads(path.read_text(encoding="utf-8")))
