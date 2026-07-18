from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import argparse
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from animation import AnimationConfig
from ascii import AsciiConfig, render_image, write_preview
from github import (
    ContributionCalendar,
    empty_calendar,
    fetch_contributions,
    load_contributions,
    save_contributions,
)
from heatmap import HeatmapConfig, render_heatmap_svg
from info_card import InfoCardConfig, InfoSection, render_info_card
from prep_photo import PhotoPrepConfig, preprocess_photo
from renderer import TerminalRenderConfig, TerminalTheme, render_terminal_svg


@dataclass(frozen=True)
class Project:
    name: str
    description: str
    stack: str


@dataclass(frozen=True)
class ProfileConfig:
    username: str = os.getenv("GITHUB_USERNAME", "sankalp03326")
    name: str = os.getenv("PROFILE_NAME", "Sankalp Varshney")
    role: str = os.getenv("PROFILE_ROLE", "Senior Software Engineer")
    tagline: str = (
        "Software Engineer | Cloud Architect | Data Science and AI/ML Enthusiast"
    )
    focus: str = (
        "Architecting enterprise platforms, cloud infrastructure, and automated delivery systems."
    )
    linkedin: str = "https://www.linkedin.com/in/sankalp-varshney8445"
    projects: tuple[Project, ...] = field(
        default_factory=lambda: (
            Project(
                "Energy Dive Ecosystem",
                "Premium media and market intelligence platform with dynamic sector experiences.",
                "React, Vite, Tailwind, PHP, MySQL",
            ),
            Project(
                "Energ Members System",
                "JWT and OTP authentication flow for secure premium content access.",
                "React, PHP, REST, Security",
            ),
            Project(
                "Cloud Operations Toolkit",
                "Deployment, monitoring, and server automation for production workloads.",
                "Linux, Docker, Nginx, GitHub Actions",
            ),
        )
    )
    tech_stack: tuple[str, ...] = (
        "Python",
        "TypeScript",
        "JavaScript",
        "React",
        "Next.js",
        "Node.js",
        "PHP",
        "PostgreSQL",
        "MySQL",
        "AWS",
        "Azure",
        "Docker",
        "Linux",
        "Nginx",
        "GitHub Actions",
    )


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _terminal_rows(config: ProfileConfig) -> list[str]:
    return [
        "$ whoami",
        config.username,
        "",
        "$ cat profile.txt",
        config.role,
        config.tagline,
        "",
        "$ ./build-profile --target github-readme",
        "[ok] ascii portrait generated",
        "[ok] terminal animation generated",
        "[ok] neofetch card generated",
        "[ok] contribution heatmap generated",
        "",
        "$ status --focus",
        config.focus,
    ]


def _build_info_config(profile: ProfileConfig, static: bool) -> InfoCardConfig:
    return InfoCardConfig(
        name=profile.name,
        username=profile.username,
        static=static,
        sections=(
            InfoSection("Name", profile.name),
            InfoSection("Role", profile.role),
            InfoSection("Frontend", "React, Next.js, TypeScript, Tailwind"),
            InfoSection("Backend", "Python, Node.js, PHP, REST"),
            InfoSection("Cloud", "AWS, Azure, DigitalOcean"),
            InfoSection("DevOps", "Docker, Linux, Nginx, GitHub Actions"),
            InfoSection("Database", "PostgreSQL, MySQL"),
            InfoSection("Learning", "Data Science, AI/ML, Kubernetes"),
            InfoSection("Languages", "Python, TypeScript, JavaScript, PHP, Bash"),
            InfoSection("Tools", "Git, VS Code, Figma, CI/CD"),
        ),
    )


def _fetch_or_load_contributions(
    username: str,
    data_path: Path,
    offline: bool,
) -> ContributionCalendar:
    if not offline:
        try:
            calendar = fetch_contributions(username)
            save_contributions(calendar, data_path)
            return calendar
        except Exception as exc:
            print(f"Warning: live contribution fetch failed: {exc}", file=sys.stderr)

    if data_path.exists():
        return load_contributions(data_path)

    calendar = empty_calendar(username)
    save_contributions(calendar, data_path)
    return calendar


def _badge(label: str) -> str:
    safe_label = label.replace(" ", "%20").replace("#", "%23")
    return (
        f'<img alt="{label}" src="https://img.shields.io/badge/'
        f'{safe_label}-161b22?style=for-the-badge&labelColor=0d1117&color=30363d" />'
    )


def render_readme(profile: ProfileConfig) -> str:
    project_rows = "\n".join(
        (
            "    <tr>\n"
            f"      <td align=\"center\"><strong>{project.name}</strong></td>\n"
            f"      <td align=\"center\">{project.description}</td>\n"
            f"      <td align=\"center\"><code>{project.stack}</code></td>\n"
            "    </tr>"
        )
        for project in profile.projects
    )
    badges = "\n    ".join(_badge(label) for label in profile.tech_stack)

    return f"""<!-- Generated by scripts/build.py -->
<div align="center">
  <h1>{profile.name}</h1>
  <p><strong>{profile.tagline}</strong></p>
  <p>{profile.focus}</p>

  <p>
    <a href="https://github.com/{profile.username}">
      <img alt="GitHub" src="https://img.shields.io/badge/GitHub-{profile.username}-161b22?style=for-the-badge&logo=github&labelColor=0d1117&color=30363d" />
    </a>
    <a href="{profile.linkedin}">
      <img alt="LinkedIn" src="https://img.shields.io/badge/LinkedIn-Connect-0a66c2?style=for-the-badge&logo=linkedin&labelColor=0d1117" />
    </a>
  </p>

  <h2>Contribution Graph</h2>
  <img src="./output/contribution-grid.svg" alt="Live GitHub contribution heatmap" />

  <h2>Terminal Window</h2>
  <img src="./output/terminal.svg" alt="Animated terminal window" />

  <h2>ASCII Portrait</h2>
  <img src="./output/portrait.svg" alt="Animated ASCII portrait" />

  <h2>Neofetch</h2>
  <img src="./output/info-card.svg" alt="Animated neofetch-style information card" />

  <h2>Projects</h2>
  <table align="center">
    <thead>
      <tr>
        <th align="center">Project</th>
        <th align="center">Focus</th>
        <th align="center">Stack</th>
      </tr>
    </thead>
    <tbody>
{project_rows}
    </tbody>
  </table>

  <h2>Tech Stack</h2>
  <p>
    {badges}
  </p>

  <h2>Social Links</h2>
  <p>
    <a href="https://github.com/{profile.username}">github.com/{profile.username}</a>
    <br />
    <a href="{profile.linkedin}">LinkedIn</a>
  </p>

  <sub>Generated daily with Python, SMIL SVG, and GitHub Actions.</sub>
</div>
"""


def build(static: bool = False, prep_photo: bool = False, offline: bool = False) -> None:
    profile = ProfileConfig()
    assets = ROOT / "assets"
    output = ROOT / "output"
    data = ROOT / "data"
    portrait = assets / "portrait.jpg"
    prepped = assets / "source-prepped.png"

    assets.mkdir(exist_ok=True)
    output.mkdir(exist_ok=True)
    data.mkdir(exist_ok=True)

    if prep_photo or not prepped.exists():
        preprocess_photo(
            PhotoPrepConfig(
                source=portrait,
                output=prepped,
                remove_background=True,
            )
        )

    ascii_rows = render_image(
        prepped,
        AsciiConfig(
            width=104,
            brightness=1.03,
            contrast=1.22,
            gamma=0.92,
            character_aspect_ratio=0.48,
        ),
    )
    write_preview(ascii_rows, output / "ascii-preview.txt")

    portrait_svg = render_terminal_svg(
        ascii_rows,
        TerminalRenderConfig(
            title="portrait.asc",
            description=f"Animated ASCII portrait for {profile.name}",
            font_size=12,
            line_height=14,
            padding_x=22,
            padding_y=18,
            min_width=840,
        ),
        AnimationConfig(
            static=static,
            initial_delay=0.15,
            line_delay=0.018,
            characters_per_second=180,
            cursor_height=14,
        ),
    )
    _write_text(output / "portrait.svg", portrait_svg)
    _write_text(output / "avi-ascii.svg", portrait_svg)

    terminal_svg = render_terminal_svg(
        _terminal_rows(profile),
        TerminalRenderConfig(
            title="profile-engine",
            description="Animated terminal profile summary",
            font_size=14,
            line_height=22,
            padding_x=26,
            padding_y=24,
            min_width=760,
            theme=TerminalTheme(text="#e6edf3"),
        ),
        AnimationConfig(
            static=static,
            initial_delay=0.25,
            line_delay=0.12,
            characters_per_second=68,
            cursor_color="#58a6ff",
            cursor_height=16,
        ),
    )
    _write_text(output / "terminal.svg", terminal_svg)

    _write_text(
        output / "info-card.svg",
        render_info_card(_build_info_config(profile, static=static)),
    )

    contribution_calendar = _fetch_or_load_contributions(
        profile.username,
        data / "contributions.json",
        offline=offline,
    )
    _write_text(
        output / "contribution-grid.svg",
        render_heatmap_svg(
            contribution_calendar,
            HeatmapConfig(title="GitHub Contribution Activity"),
        ),
    )

    _write_text(ROOT / "README.md", render_readme(profile))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the GitHub profile README assets.")
    parser.add_argument("--static", action="store_true", help="Disable SMIL animations.")
    parser.add_argument("--prep-photo", action="store_true", help="Regenerate assets/source-prepped.png.")
    parser.add_argument("--offline", action="store_true", help="Use cached contribution data.")
    args = parser.parse_args()

    build(static=args.static, prep_photo=args.prep_photo, offline=args.offline)
    print("Generated README.md and output SVG assets.")


if __name__ == "__main__":
    main()
