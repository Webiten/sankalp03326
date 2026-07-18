from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from html import escape
from pathlib import Path

from github import ContributionCalendar, ContributionDay, LEVEL_COLORS, compute_stats, load_contributions


WEEKDAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


@dataclass(frozen=True)
class HeatmapTheme:
    background: str = "#0d1117"
    border: str = "#30363d"
    text: str = "#e6edf3"
    muted: str = "#8b949e"
    accent: str = "#58a6ff"
    level_colors: dict[int, str] = field(default_factory=lambda: LEVEL_COLORS.copy())


@dataclass(frozen=True)
class HeatmapConfig:
    title: str = "GitHub Contribution Activity"
    cell_size: int = 11
    gap: int = 3
    radius: int = 2
    padding: int = 24
    left_label_width: int = 34
    top_offset: int = 74
    bottom_offset: int = 82
    min_width: int = 640
    theme: HeatmapTheme = field(default_factory=HeatmapTheme)


def _github_weekday(day: date) -> int:
    return (day.weekday() + 1) % 7


def _week_start(day: date) -> date:
    return day - timedelta(days=_github_weekday(day))


def _display_color(day: ContributionDay, theme: HeatmapTheme) -> str:
    if day.color and day.color != "#ebedf0" and not day.color.startswith("var("):
        return day.color
    return theme.level_colors.get(day.level, theme.level_colors[0])


def render_heatmap_svg(
    contribution_calendar: ContributionCalendar,
    config: HeatmapConfig | None = None,
) -> str:
    config = config or HeatmapConfig()
    days = sorted(contribution_calendar.days, key=lambda item: item.date)
    stats = compute_stats(days)

    if not days:
        days = []
        start = date.today()
        end = start
    else:
        start = _week_start(days[0].date)
        end = days[-1].date

    week_count = ((end - start).days // 7) + 1
    grid_x = config.padding + config.left_label_width
    grid_y = config.top_offset
    grid_width = week_count * (config.cell_size + config.gap) - config.gap
    grid_height = 7 * (config.cell_size + config.gap) - config.gap
    width = max(config.min_width, grid_x + grid_width + config.padding)
    height = grid_y + grid_height + config.bottom_offset
    font_family = "JetBrains Mono, SFMono-Regular, Consolas, Liberation Mono, monospace"

    by_date = {day.date: day for day in days}
    cells: list[str] = []

    for contribution_day in days:
        week = (contribution_day.date - start).days // 7
        weekday = _github_weekday(contribution_day.date)
        x = grid_x + week * (config.cell_size + config.gap)
        y = grid_y + weekday * (config.cell_size + config.gap)
        title = (
            f"{contribution_day.count} contribution"
            f"{'' if contribution_day.count == 1 else 's'} on {contribution_day.date.isoformat()}"
        )
        cells.extend(
            [
                (
                    f'<rect x="{x}" y="{y}" width="{config.cell_size}" '
                    f'height="{config.cell_size}" rx="{config.radius}" '
                    f'fill="{_display_color(contribution_day, config.theme)}">'
                ),
                f"<title>{escape(title)}</title>",
                "</rect>",
            ]
        )

    month_labels: list[str] = []
    cursor = date(start.year, start.month, 1)
    while cursor <= end:
        if cursor >= days[0].date if days else True:
            week = (cursor - start).days // 7
            x = grid_x + week * (config.cell_size + config.gap)
            month_labels.append(
                (
                    f'<text x="{x}" y="{grid_y - 12}" font-family="{font_family}" '
                    f'font-size="10" fill="{config.theme.muted}">{cursor.strftime("%b")}</text>'
                )
            )
        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)

    weekday_labels = [
        (
            f'<text x="{config.padding}" y="{grid_y + index * (config.cell_size + config.gap) + 9}" '
            f'font-family="{font_family}" font-size="10" fill="{config.theme.muted}">{label}</text>'
        )
        for index, label in enumerate(WEEKDAY_LABELS)
        if index in {1, 3, 5}
    ]

    stat_y = grid_y + grid_height + 34
    source_label = "live from GitHub" if contribution_calendar.source.startswith("https://") else "offline cache"
    active_days = sum(1 for day in by_date.values() if day.count > 0)
    stats_text = (
        f'{stats.total_contributions:,} total | {stats.current_streak} current streak | '
        f'{stats.longest_streak} longest | {stats.average_per_day:.2f}/day | '
        f'{stats.most_active_weekday} peak | {active_days} active days'
    )

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" '
            'aria-labelledby="contribution-title contribution-desc" '
            'style="max-width:100%;height:auto;">'
        ),
        f'<title id="contribution-title">{escape(config.title)}</title>',
        (
            f'<desc id="contribution-desc">Contribution heatmap for '
            f'{escape(contribution_calendar.username)}.</desc>'
        ),
        f'<rect width="{width}" height="{height}" rx="10" fill="{config.theme.background}" />',
        (
            f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" '
            f'rx="10" fill="none" stroke="{config.theme.border}" />'
        ),
        (
            f'<text x="{config.padding}" y="32" font-family="{font_family}" '
            f'font-size="18" font-weight="700" fill="{config.theme.text}">{escape(config.title)}</text>'
        ),
        (
            f'<text x="{config.padding}" y="54" font-family="{font_family}" '
            f'font-size="12" fill="{config.theme.muted}">@{escape(contribution_calendar.username)} '
            f'- {escape(source_label)}</text>'
        ),
        *month_labels,
        *weekday_labels,
        *cells,
        (
            f'<text x="{config.padding}" y="{stat_y}" font-family="{font_family}" '
            f'font-size="12" fill="{config.theme.text}">{escape(stats_text)}</text>'
        ),
        (
            f'<text x="{config.padding}" y="{stat_y + 22}" font-family="{font_family}" '
            f'font-size="11" fill="{config.theme.muted}">Generated '
            f'{escape(contribution_calendar.fetched_at.date().isoformat())}</text>'
        ),
        "</svg>",
    ]
    return "\n".join(parts) + "\n"


def render_heatmap_from_json(path: Path, config: HeatmapConfig | None = None) -> str:
    return render_heatmap_svg(load_contributions(path), config=config)
