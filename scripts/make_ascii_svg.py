from __future__ import annotations

from pathlib import Path

from animation import AnimationConfig
from ascii import AsciiConfig, render_image, write_preview
from renderer import TerminalRenderConfig, render_terminal_svg


def main() -> None:
    input_path = Path("assets/source-prepped.png")
    preview_path = Path("output/ascii-preview.txt")
    svg_path = Path("output/portrait.svg")
    legacy_svg_path = Path("output/avi-ascii.svg")

    rows = render_image(input_path, AsciiConfig(width=100))
    write_preview(rows, preview_path)
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg = render_terminal_svg(
        rows,
        TerminalRenderConfig(
            title="portrait.asc",
            description="Animated ASCII portrait",
            min_width=840,
        ),
        AnimationConfig(characters_per_second=180, line_delay=0.02),
    )
    svg_path.write_text(svg, encoding="utf-8")
    legacy_svg_path.write_text(svg, encoding="utf-8")
    print(f"ASCII preview: {preview_path}")
    print(f"SVG: {svg_path}")


if __name__ == "__main__":
    main()
