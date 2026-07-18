from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from html import escape
from pathlib import Path

from github import ContributionCalendar, ContributionDay, LEVEL_COLORS, load_contributions
from stats import summarize_activity
from utils import (
    PALETTE,
    ProfileData,
    SvgDocument,
    background_layer,
    circle,
    cyberpunk_defs,
    glass_panel,
    icon,
    line,
    metric_card,
    pretty_int,
    rect,
    section_header,
    text_element,
)


WEEKDAY_LABELS = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")


@dataclass(frozen=True)
class HeatmapTheme:
    background: str = PALETTE.background
    border: str = PALETTE.border
    text: str = PALETTE.text
    muted: str = PALETTE.muted
    accent: str = PALETTE.green
    level_colors: dict[int, str] = field(
        default_factory=lambda: {
            0: "#111827",
            1: "#0A3D2B",
            2: "#00875A",
            3: "#00C781",
            4: "#00FF88",
        }
    )


@dataclass(frozen=True)
class HeatmapConfig:
    title: str = "Contribution Grid"
    cell_size: int = 10
    gap: int = 3
    radius: int = 2
    width: int = 1200
    height: int = 470
    theme: HeatmapTheme = field(default_factory=HeatmapTheme)


def _github_weekday(day: date) -> int:
    return (day.weekday() + 1) % 7


def _week_start(day: date) -> date:
    return day - timedelta(days=_github_weekday(day))


def _display_color(day: ContributionDay, theme: HeatmapTheme) -> str:
    if day.color and day.color != "#ebedf0" and not day.color.startswith("var("):
        return day.color
    return theme.level_colors.get(day.level, theme.level_colors[0])


def _calendar_bounds(days: list[ContributionDay]) -> tuple[date, date, int]:
    if not days:
        today = date.today()
        return _week_start(today - timedelta(days=370)), today, 53

    start = _week_start(days[0].date)
    end = days[-1].date
    week_count = ((end - start).days // 7) + 1
    return start, end, week_count


def _month_labels(
    days: list[ContributionDay],
    *,
    start: date,
    end: date,
    grid_x: int,
    grid_y: int,
    cell_size: int,
    gap: int,
) -> list[str]:
    if not days:
        return []

    labels: list[str] = []
    cursor = date(days[0].date.year, days[0].date.month, 1)
    while cursor <= end:
        if cursor >= days[0].date:
            week = (cursor - start).days // 7
            x = grid_x + week * (cell_size + gap)
            labels.append(
                text_element(
                    x,
                    grid_y - 14,
                    cursor.strftime("%b"),
                    size=11,
                    fill=PALETTE.muted,
                    family="JetBrains Mono, monospace",
                )
            )

        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)

    return labels


def _render_cells(
    doc: SvgDocument,
    days: list[ContributionDay],
    *,
    start: date,
    grid_x: int,
    grid_y: int,
    cell_size: int,
    gap: int,
    theme: HeatmapTheme,
) -> None:
    for index, contribution_day in enumerate(days):
        week = (contribution_day.date - start).days // 7
        weekday = _github_weekday(contribution_day.date)
        x = grid_x + week * (cell_size + gap)
        y = grid_y + weekday * (cell_size + gap)
        title = (
            f"{contribution_day.count} contribution"
            f"{'' if contribution_day.count == 1 else 's'} on {contribution_day.date.isoformat()}"
        )
        color = _display_color(contribution_day, theme)
        glow = f' filter="url(#{doc.id_prefix}-glow)"' if contribution_day.level >= 3 else ""
        delay = 0.02 + (index % 53) * 0.012
        doc.add(
            f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
            f'rx="{theme.level_colors and 2}" fill="{color}" opacity="0.25"{glow}>'
            f"<title>{escape(title)}</title>"
            f'<animate attributeName="opacity" from="0.20" to="{0.92 if contribution_day.level else 0.52}" '
            f'begin="{delay:.3f}s" dur="0.700s" fill="freeze" />'
            "</rect>"
        )


def _render_legend(doc: SvgDocument, x: int, y: int, theme: HeatmapTheme) -> None:
    doc.add(text_element(x, y + 12, "Less", size=11, fill=PALETTE.muted, family="JetBrains Mono, monospace"))
    for level in range(5):
        doc.add(rect(x + 42 + level * 18, y, 11, 11, rx=2, fill=theme.level_colors[level], stroke=PALETTE.border, stroke_width=0.7))
    doc.add(text_element(x + 140, y + 12, "More", size=11, fill=PALETTE.muted, family="JetBrains Mono, monospace"))


def _render_side_panel(
    doc: SvgDocument,
    profile: ProfileData,
    calendar: ContributionCalendar,
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    summary = summarize_activity(calendar)
    glass_panel(doc, x, y, width, height, radius=18, accent=PALETTE.cyan, glow=False)
    doc.add(text_element(x + 28, y + 34, "COMMIT TELEMETRY", size=11, fill=PALETTE.cyan, weight=850, family="JetBrains Mono, monospace"))
    doc.add(text_element(x + 28, y + 70, f"@{profile.username}", size=24, fill=PALETTE.text, weight=850))
    doc.add(text_element(x + 28, y + 94, "Contribution data parsed from public GitHub graph.", size=12, fill=PALETTE.muted, family="JetBrains Mono, monospace"))

    metric_card(doc, x + 24, y + 122, 170, 88, label="Total", value=pretty_int(summary.stats.total_contributions), accent=PALETTE.green, icon_name="github", delay=0.18)
    metric_card(doc, x + 210, y + 122, 170, 88, label="Week", value=str(summary.this_week), accent=PALETTE.cyan, icon_name="bolt", delay=0.28)
    metric_card(doc, x + 24, y + 226, 170, 88, label="Month", value=str(summary.this_month), accent=PALETTE.purple, icon_name="api", delay=0.38)
    metric_card(doc, x + 210, y + 226, 170, 88, label="Active days", value=str(summary.active_days), accent=PALETTE.pink, icon_name="calendar", delay=0.48)

    best_day = "No activity yet"
    if summary.best_day and summary.best_day.count > 0:
        best_day = f"{summary.best_day.count} on {summary.best_day.date.isoformat()}"
    doc.add(line(x + 28, y + 338, x + width - 28, y + 338, stroke=PALETTE.border, stroke_width=1))
    doc.add(icon("devops", x + 28, y + 354, 22, PALETTE.amber))
    doc.add(text_element(x + 62, y + 370, f"Longest streak: {summary.stats.longest_streak} days", size=13, fill=PALETTE.text, weight=700, family="JetBrains Mono, monospace"))
    doc.add(text_element(x + 62, y + 394, f"Best day: {best_day}", size=12, fill=PALETTE.muted, family="JetBrains Mono, monospace"))


def render_contributions_svg(
    profile: ProfileData,
    contribution_calendar: ContributionCalendar,
    config: HeatmapConfig | None = None,
) -> str:
    config = config or HeatmapConfig()
    days = sorted(contribution_calendar.days, key=lambda item: item.date)
    start, end, week_count = _calendar_bounds(days)

    doc = SvgDocument(
        width=config.width,
        height=config.height,
        title=f"{profile.name} contribution heatmap",
        description="Custom animated contribution heatmap generated from public GitHub contribution markup.",
        id_prefix="contrib",
    )
    doc.extend(cyberpunk_defs(doc.id_prefix))
    background_layer(doc)
    section_header(doc, 42, 44, kicker="contribution grid", title=config.title, accent=PALETTE.green)

    grid_x = 58
    grid_y = 142
    grid_width = week_count * (config.cell_size + config.gap) - config.gap
    grid_height = 7 * (config.cell_size + config.gap) - config.gap
    panel_width = grid_width + 78
    glass_panel(doc, 32, 108, panel_width, 240, radius=18, accent=PALETTE.green, glow=False)
    doc.extend(
        _month_labels(
            days,
            start=start,
            end=end,
            grid_x=grid_x,
            grid_y=grid_y,
            cell_size=config.cell_size,
            gap=config.gap,
        )
    )

    for index, label in enumerate(WEEKDAY_LABELS):
        if index in (1, 3, 5):
            doc.add(text_element(42, grid_y + index * (config.cell_size + config.gap) + 10, label, size=10, fill=PALETTE.muted, family="JetBrains Mono, monospace"))

    _render_cells(
        doc,
        days,
        start=start,
        grid_x=grid_x,
        grid_y=grid_y,
        cell_size=config.cell_size,
        gap=config.gap,
        theme=config.theme,
    )
    _render_legend(doc, 58, grid_y + grid_height + 34, config.theme)
    doc.add(circle(292, grid_y + grid_height + 39, 4, fill=PALETTE.green, opacity=0.92, filter_=f"url(#{doc.id_prefix}-glow)"))
    doc.add(text_element(306, grid_y + grid_height + 43, f"Fetched {contribution_calendar.fetched_at.date().isoformat()}", size=11, fill=PALETTE.muted, family="JetBrains Mono, monospace"))

    _render_side_panel(doc, profile, contribution_calendar, 770, 44, 388, 382)
    return doc.document()


def render_heatmap_svg(
    contribution_calendar: ContributionCalendar,
    config: HeatmapConfig | None = None,
) -> str:
    profile = ProfileData(
        username=contribution_calendar.username,
        name=contribution_calendar.username,
        role="Software Engineer",
        subtitle="GitHub activity",
        focus="Contribution activity",
        location="",
        email="",
        portfolio=f"https://github.com/{contribution_calendar.username}",
        linkedin="",
        twitter="",
        status="",
        social=(),
        skill_categories=(),
        projects=(),
        tech_stack=(),
        learning=(),
    )
    return render_contributions_svg(profile, contribution_calendar, config=config)


def render_heatmap_from_json(path: Path, config: HeatmapConfig | None = None) -> str:
    return render_heatmap_svg(load_contributions(path), config=config)
