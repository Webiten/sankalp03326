from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from github import ContributionCalendar, ContributionDay, ContributionStats, compute_stats
from utils import (
    PALETTE,
    ProfileData,
    SvgDocument,
    background_layer,
    cyberpunk_defs,
    glass_panel,
    metric_card,
    pretty_int,
    progress_bar,
    section_header,
    text_element,
)


@dataclass(frozen=True)
class ActivitySummary:
    stats: ContributionStats
    active_days: int
    best_day: ContributionDay | None
    this_week: int
    this_month: int
    last_30_days: int
    weekday_totals: tuple[int, int, int, int, int, int, int]
    month_series: tuple[tuple[str, int], ...]


def summarize_activity(calendar: ContributionCalendar) -> ActivitySummary:
    ordered_days = tuple(sorted(calendar.days, key=lambda item: item.date))
    stats = compute_stats(list(ordered_days))

    if not ordered_days:
        return ActivitySummary(
            stats=stats,
            active_days=0,
            best_day=None,
            this_week=0,
            this_month=0,
            last_30_days=0,
            weekday_totals=(0, 0, 0, 0, 0, 0, 0),
            month_series=(),
        )

    end_date = ordered_days[-1].date
    week_start = end_date - timedelta(days=end_date.weekday())
    month_start = date(end_date.year, end_date.month, 1)
    thirty_days_ago = end_date - timedelta(days=29)
    weekday_totals = [0, 0, 0, 0, 0, 0, 0]
    active_days = 0
    best_day = ordered_days[0]
    month_totals: dict[str, int] = {}

    this_week = 0
    this_month = 0
    last_30_days = 0

    for day in ordered_days:
        if day.count > 0:
            active_days += 1
        if day.count > best_day.count:
            best_day = day
        if day.date >= week_start:
            this_week += day.count
        if day.date >= month_start:
            this_month += day.count
        if day.date >= thirty_days_ago:
            last_30_days += day.count

        weekday_totals[day.date.weekday()] += day.count
        month_key = day.date.strftime("%b")
        month_totals[month_key] = month_totals.get(month_key, 0) + day.count

    return ActivitySummary(
        stats=stats,
        active_days=active_days,
        best_day=best_day,
        this_week=this_week,
        this_month=this_month,
        last_30_days=last_30_days,
        weekday_totals=tuple(weekday_totals),
        month_series=tuple(month_totals.items()),
    )


def _weekday_panel(doc: SvgDocument, summary: ActivitySummary, x: int, y: int, width: int) -> None:
    labels = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    max_value = max(summary.weekday_totals, default=0) or 1
    row_height = 26

    for index, (label, value) in enumerate(zip(labels, summary.weekday_totals)):
        row_y = y + index * row_height
        doc.add(text_element(x, row_y + 16, label, size=11, fill=PALETTE.muted, family="JetBrains Mono, monospace"))
        progress_bar(
            doc,
            x + 42,
            row_y + 4,
            width - 86,
            10,
            (value / max_value) * 100,
            accent=(PALETTE.cyan if index % 2 == 0 else PALETTE.purple),
            delay=0.2 + index * 0.08,
            label=str(value),
        )


def _month_activity(doc: SvgDocument, summary: ActivitySummary, x: int, y: int, width: int) -> None:
    series = summary.month_series[-12:]
    max_value = max((value for _, value in series), default=0) or 1
    bar_gap = 8
    bar_width = max(12, (width - (len(series) - 1) * bar_gap) / max(1, len(series)))
    chart_height = 122

    for index, (label, value) in enumerate(series):
        height = max(6, chart_height * (value / max_value))
        x_pos = x + index * (bar_width + bar_gap)
        y_pos = y + chart_height - height
        doc.add(
            f'<rect x="{x_pos:.1f}" y="{y + chart_height - 6:.1f}" width="{bar_width:.1f}" '
            f'height="6" rx="3" fill="{PALETTE.surface_2}" stroke="{PALETTE.border}" />'
        )
        doc.add(
            f'<rect x="{x_pos:.1f}" y="{y + chart_height:.1f}" width="{bar_width:.1f}" '
            f'height="0" rx="4" fill="{PALETTE.green}" opacity="0.88" filter="url(#{doc.id_prefix}-glow)">'
            f'<animate attributeName="y" from="{y + chart_height:.1f}" to="{y_pos:.1f}" '
            f'begin="{0.35 + index * 0.06:.3f}s" dur="1.100s" fill="freeze" />'
            f'<animate attributeName="height" from="0" to="{height:.1f}" '
            f'begin="{0.35 + index * 0.06:.3f}s" dur="1.100s" fill="freeze" />'
            "</rect>"
        )
        doc.add(text_element(x_pos + bar_width / 2, y + chart_height + 22, label, size=10, fill=PALETTE.muted, anchor="middle", family="JetBrains Mono, monospace"))


def render_stats_svg(
    profile: ProfileData,
    calendar: ContributionCalendar,
    *,
    static: bool = False,
) -> str:
    summary = summarize_activity(calendar)
    width = 1200
    height = 420
    doc = SvgDocument(
        width=width,
        height=height,
        title=f"{profile.name} GitHub activity statistics",
        description="Animated cyberpunk GitHub activity statistics dashboard.",
        id_prefix="stats",
    )
    doc.extend(cyberpunk_defs(doc.id_prefix))
    background_layer(doc)
    section_header(doc, 42, 44, kicker="live telemetry", title="GitHub Activity Matrix", accent=PALETTE.green)

    metric_card(
        doc,
        42,
        126,
        252,
        104,
        label="Total contributions",
        value=pretty_int(summary.stats.total_contributions),
        accent=PALETTE.cyan,
        icon_name="github",
        delay=0.10,
    )
    metric_card(
        doc,
        318,
        126,
        252,
        104,
        label="Current streak",
        value=f"{summary.stats.current_streak} days",
        accent=PALETTE.green,
        icon_name="bolt",
        delay=0.25,
    )
    metric_card(
        doc,
        594,
        126,
        252,
        104,
        label="Longest streak",
        value=f"{summary.stats.longest_streak} days",
        accent=PALETTE.purple,
        icon_name="devops",
        delay=0.40,
    )
    metric_card(
        doc,
        870,
        126,
        288,
        104,
        label="Average per day",
        value=f"{summary.stats.average_per_day:.2f}",
        accent=PALETTE.amber,
        icon_name="api",
        delay=0.55,
    )

    glass_panel(doc, 42, 258, 526, 120, radius=18, accent=PALETTE.pink, glow=False)
    doc.add(text_element(70, 292, "CURRENT WINDOW", size=11, fill=PALETTE.pink, weight=800, family="JetBrains Mono, monospace"))
    doc.add(text_element(70, 330, f"{summary.this_week} this week", size=24, fill=PALETTE.text, weight=850, family="JetBrains Mono, monospace"))
    doc.add(text_element(306, 330, f"{summary.this_month} this month", size=24, fill=PALETTE.text, weight=850, family="JetBrains Mono, monospace"))
    best_label = "none recorded"
    if summary.best_day and summary.best_day.count > 0:
        best_label = f"{summary.best_day.count} on {summary.best_day.date.isoformat()}"
    doc.add(text_element(70, 358, f"Best day: {best_label}", size=13, fill=PALETTE.muted, family="JetBrains Mono, monospace"))
    doc.add(text_element(306, 358, f"Most active: {summary.stats.most_active_weekday}", size=13, fill=PALETTE.muted, family="JetBrains Mono, monospace"))

    glass_panel(doc, 594, 258, 250, 120, radius=18, accent=PALETTE.cyan, glow=False)
    doc.add(text_element(622, 292, "WEEKDAY SIGNAL", size=11, fill=PALETTE.cyan, weight=800, family="JetBrains Mono, monospace"))
    _weekday_panel(doc, summary, 622, 306, 190)

    glass_panel(doc, 870, 258, 288, 120, radius=18, accent=PALETTE.green, glow=False)
    doc.add(text_element(898, 292, "MONTHLY ACTIVITY", size=11, fill=PALETTE.green, weight=800, family="JetBrains Mono, monospace"))
    _month_activity(doc, summary, 898, 306, 232)

    return doc.document()
