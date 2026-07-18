from __future__ import annotations

from dataclasses import dataclass, field

from animation import AnimationConfig
from renderer import TerminalRenderConfig, TerminalTheme, render_terminal_svg


@dataclass(frozen=True)
class InfoSection:
    label: str
    value: str


@dataclass(frozen=True)
class InfoCardConfig:
    name: str = "Sankalp Varshney"
    username: str = "sankalp03326"
    host: str = "github"
    accent: str = "#58a6ff"
    sections: tuple[InfoSection, ...] = field(
        default_factory=lambda: (
            InfoSection("Role", "Senior Software Engineer"),
            InfoSection("Frontend", "React, Next.js, TypeScript, Tailwind"),
            InfoSection("Backend", "Python, Node.js, PHP, REST"),
            InfoSection("Cloud", "AWS, Azure, DigitalOcean"),
            InfoSection("DevOps", "Docker, Linux, Nginx, GitHub Actions"),
            InfoSection("Database", "PostgreSQL, MySQL"),
            InfoSection("Learning", "Data Science, AI/ML, Kubernetes"),
            InfoSection("Languages", "Python, TypeScript, JavaScript, PHP, Bash"),
            InfoSection("Tools", "Git, VS Code, Figma, CI/CD"),
        )
    )
    static: bool = False


def build_info_rows(config: InfoCardConfig) -> list[str]:
    header = f"{config.username}@{config.host}"
    divider = "-" * len(header)
    label_width = max(len(section.label) for section in config.sections)
    rows = [header, divider]

    for section in config.sections:
        rows.append(f"{section.label.ljust(label_width)} : {section.value}")

    return rows


def render_info_card(config: InfoCardConfig | None = None) -> str:
    config = config or InfoCardConfig()
    rows = build_info_rows(config)
    theme = TerminalTheme(
        background="#0d1117",
        panel="#0d1117",
        header="#161b22",
        border="#30363d",
        text="#e6edf3",
        muted="#8b949e",
    )
    return render_terminal_svg(
        rows,
        TerminalRenderConfig(
            title="neofetch",
            description=f"Neofetch-style profile card for {config.name}",
            font_size=13,
            line_height=20,
            padding_x=26,
            padding_y=24,
            min_width=690,
            theme=theme,
        ),
        AnimationConfig(
            static=config.static,
            initial_delay=0.2,
            line_delay=0.08,
            characters_per_second=70,
            cursor_color=config.accent,
            cursor_height=15,
        ),
    )
