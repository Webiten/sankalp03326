from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha1
from html import escape
from math import ceil

from animation import AnimationConfig, TextLayout, render_animated_text, render_static_text


@dataclass(frozen=True)
class TerminalTheme:
    background: str = "#0d1117"
    panel: str = "#0d1117"
    header: str = "#161b22"
    border: str = "#30363d"
    text: str = "#d4d4d4"
    muted: str = "#8b949e"
    red: str = "#ff5f56"
    yellow: str = "#ffbd2e"
    green: str = "#27c93f"


@dataclass(frozen=True)
class TerminalRenderConfig:
    title: str = "profile.sh"
    description: str = "Generated terminal SVG"
    font_family: str = "JetBrains Mono, SFMono-Regular, Consolas, Liberation Mono, monospace"
    font_size: int = 12
    line_height: int = 14
    char_width: float | None = None
    padding_x: int = 24
    padding_y: int = 20
    header_height: int = 38
    corner_radius: int = 10
    min_width: int = 360
    theme: TerminalTheme = field(default_factory=TerminalTheme)

    def resolved_char_width(self) -> float:
        return self.char_width if self.char_width is not None else self.font_size * 0.62


def _svg_id(value: str) -> str:
    digest = sha1(value.encode("utf-8")).hexdigest()[:10]
    return f"svg-{digest}"


def measure_svg(rows: list[str], config: TerminalRenderConfig) -> tuple[int, int, float]:
    columns = max((len(row) for row in rows), default=0)
    char_width = config.resolved_char_width()
    content_width = ceil(columns * char_width)
    width = max(config.min_width, content_width + config.padding_x * 2)
    height = (
        config.header_height
        + config.padding_y * 2
        + max(1, len(rows)) * config.line_height
    )
    return width, height, char_width


def render_terminal_svg(
    rows: list[str],
    config: TerminalRenderConfig | None = None,
    animation: AnimationConfig | None = None,
) -> str:
    config = config or TerminalRenderConfig()
    width, height, char_width = measure_svg(rows, config)
    root_id = _svg_id(config.title + "\n" + "\n".join(rows))
    title_id = f"{root_id}-title"
    desc_id = f"{root_id}-desc"
    text_y = config.header_height + config.padding_y + config.font_size
    layout = TextLayout(
        x=config.padding_x,
        first_baseline=text_y,
        font_size=config.font_size,
        line_height=config.line_height,
        char_width=char_width,
        font_family=config.font_family,
        fill=config.theme.text,
    )

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
            f'aria-labelledby="{title_id} {desc_id}" '
            'style="max-width:100%;height:auto;">'
        ),
        f'<title id="{title_id}">{escape(config.title)}</title>',
        f'<desc id="{desc_id}">{escape(config.description)}</desc>',
        f'<rect width="{width}" height="{height}" fill="{config.theme.background}" rx="{config.corner_radius}" />',
        (
            f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" '
            f'rx="{config.corner_radius}" fill="{config.theme.panel}" '
            f'stroke="{config.theme.border}" />'
        ),
        (
            f'<path d="M {config.corner_radius} 0 H {width - config.corner_radius} '
            f'Q {width} 0 {width} {config.corner_radius} V {config.header_height} '
            f'H 0 V {config.corner_radius} Q 0 0 {config.corner_radius} 0 Z" '
            f'fill="{config.theme.header}" />'
        ),
        f'<line x1="0" y1="{config.header_height}" x2="{width}" y2="{config.header_height}" stroke="{config.theme.border}" />',
        f'<circle cx="20" cy="19" r="5.5" fill="{config.theme.red}" />',
        f'<circle cx="38" cy="19" r="5.5" fill="{config.theme.yellow}" />',
        f'<circle cx="56" cy="19" r="5.5" fill="{config.theme.green}" />',
        (
            f'<text x="{width / 2:.1f}" y="24" text-anchor="middle" '
            f'font-family="{escape(config.font_family, quote=True)}" '
            f'font-size="12" fill="{config.theme.muted}">{escape(config.title)}</text>'
        ),
    ]

    if animation is not None and not animation.static:
        defs, body = render_animated_text(rows, layout, animation, root_id)
        parts.extend(defs)
        parts.extend(body)
    else:
        parts.extend(render_static_text(rows, layout))

    parts.append("</svg>")
    return "\n".join(parts) + "\n"
