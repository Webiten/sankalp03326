from __future__ import annotations

from dataclasses import dataclass
from html import escape


STATIC = False


@dataclass(frozen=True)
class AnimationConfig:
    static: bool = STATIC
    initial_delay: float = 0.35
    line_delay: float = 0.045
    characters_per_second: float = 95.0
    min_line_duration: float = 0.12
    cursor: bool = True
    cursor_width: int = 7
    cursor_height: int = 14
    cursor_gap: int = 3
    cursor_color: str = "#e6edf3"

    def validate(self) -> None:
        if self.initial_delay < 0:
            raise ValueError("Initial delay cannot be negative")
        if self.line_delay < 0:
            raise ValueError("Line delay cannot be negative")
        if self.characters_per_second <= 0:
            raise ValueError("Characters per second must be greater than zero")
        if self.min_line_duration <= 0:
            raise ValueError("Minimum line duration must be greater than zero")
        if self.cursor_width <= 0 or self.cursor_height <= 0:
            raise ValueError("Cursor dimensions must be greater than zero")


@dataclass(frozen=True)
class TextLayout:
    x: float
    first_baseline: float
    font_size: int
    line_height: int
    char_width: float
    font_family: str
    fill: str


def format_seconds(value: float) -> str:
    return f"{value:.3f}s"


def _line_duration(row: str, config: AnimationConfig) -> float:
    visible_characters = max(1, len(row.rstrip()) or len(row))
    return max(config.min_line_duration, visible_characters / config.characters_per_second)


def line_timings(rows: list[str], config: AnimationConfig) -> list[tuple[float, float]]:
    config.validate()
    timings: list[tuple[float, float]] = []
    cursor = config.initial_delay

    for row in rows:
        duration = _line_duration(row, config)
        timings.append((cursor, duration))
        cursor += duration + config.line_delay

    return timings


def total_duration(rows: list[str], config: AnimationConfig) -> float:
    timings = line_timings(rows, config)
    if not timings:
        return config.initial_delay

    start, duration = timings[-1]
    return start + duration


def render_static_text(rows: list[str], layout: TextLayout) -> list[str]:
    if not rows:
        return []

    first_row = escape(rows[0], quote=False)
    output = [
        (
            f'<text x="{layout.x:.1f}" y="{layout.first_baseline:.1f}" '
            f'font-family="{escape(layout.font_family, quote=True)}" '
            f'font-size="{layout.font_size}" fill="{layout.fill}" '
            'xml:space="preserve">'
        ),
        first_row,
    ]

    for row in rows[1:]:
        output.append(
            f'<tspan x="{layout.x:.1f}" dy="{layout.line_height}">'
            f"{escape(row, quote=False)}</tspan>"
        )

    output.append("</text>")
    return output


def render_animated_text(
    rows: list[str],
    layout: TextLayout,
    config: AnimationConfig,
    id_prefix: str,
) -> tuple[list[str], list[str]]:
    config.validate()
    if config.static:
        return [], render_static_text(rows, layout)

    timings = line_timings(rows, config)
    defs: list[str] = ["<defs>"]
    body: list[str] = []

    for index, row in enumerate(rows):
        baseline = layout.first_baseline + index * layout.line_height
        clip_y = baseline - layout.font_size - 2
        target_width = max(layout.char_width, len(row.rstrip()) * layout.char_width)
        begin, duration = timings[index]
        clip_id = f"{id_prefix}-clip-{index}"

        defs.extend(
            [
                f'<clipPath id="{clip_id}">',
                (
                    f'<rect x="{layout.x:.1f}" y="{clip_y:.1f}" '
                    f'width="0" height="{layout.line_height + 4}">'
                ),
                (
                    f'<animate attributeName="width" from="0" '
                    f'to="{target_width:.1f}" begin="{format_seconds(begin)}" '
                    f'dur="{format_seconds(duration)}" fill="freeze" />'
                ),
                "</rect>",
                "</clipPath>",
            ]
        )

        body.extend(
            [
                f'<g clip-path="url(#{clip_id})" opacity="0">',
                (
                    f'<animate attributeName="opacity" from="0" to="1" '
                    f'begin="{format_seconds(begin)}" dur="0.010s" fill="freeze" />'
                ),
                (
                    f'<text x="{layout.x:.1f}" y="{baseline:.1f}" '
                    f'font-family="{escape(layout.font_family, quote=True)}" '
                    f'font-size="{layout.font_size}" fill="{layout.fill}" '
                    f'xml:space="preserve">{escape(row, quote=False)}</text>'
                ),
                "</g>",
            ]
        )

    defs.append("</defs>")

    if config.cursor and rows:
        last_index = len(rows) - 1
        last_row = rows[-1].rstrip()
        baseline = layout.first_baseline + last_index * layout.line_height
        cursor_x = layout.x + len(last_row) * layout.char_width + config.cursor_gap
        cursor_y = baseline - config.cursor_height + 1
        begin = total_duration(rows, config) + config.line_delay
        body.extend(
            [
                (
                    f'<rect x="{cursor_x:.1f}" y="{cursor_y:.1f}" '
                    f'width="{config.cursor_width}" height="{config.cursor_height}" '
                    f'rx="1.5" fill="{config.cursor_color}" opacity="0">'
                ),
                (
                    f'<animate attributeName="opacity" values="1;0;1" '
                    f'begin="{format_seconds(begin)}" dur="1s" '
                    'repeatCount="indefinite" />'
                ),
                "</rect>",
            ]
        )

    return defs, body
