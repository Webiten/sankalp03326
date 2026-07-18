from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from hashlib import sha1
from html import escape
from math import ceil
import re
from typing import Iterable, Sequence


FONT_STACK = "Inter, JetBrains Mono, IBM Plex Mono, SFMono-Regular, Consolas, monospace"
MONO_FONT_STACK = "JetBrains Mono, IBM Plex Mono, SFMono-Regular, Consolas, monospace"


@dataclass(frozen=True)
class CyberpunkPalette:
    background: str = "#0D1117"
    background_2: str = "#090D14"
    surface: str = "#111827"
    surface_2: str = "#161B22"
    border: str = "#30363D"
    border_hot: str = "#00F5FF"
    text: str = "#E6EDF3"
    muted: str = "#8B949E"
    faint: str = "#586069"
    cyan: str = "#00F5FF"
    purple: str = "#8A2EFF"
    green: str = "#00FF88"
    amber: str = "#FFB800"
    pink: str = "#FF4D6D"
    blue: str = "#58A6FF"
    shadow: str = "#010409"


PALETTE = CyberpunkPalette()


@dataclass(frozen=True)
class SocialProfile:
    label: str
    value: str
    href: str
    icon: str
    accent: str


@dataclass(frozen=True)
class SkillMetric:
    name: str
    level: int
    accent: str
    icon: str
    detail: str = ""

    def normalized_level(self) -> int:
        return max(0, min(100, self.level))


@dataclass(frozen=True)
class SkillCategory:
    title: str
    icon: str
    accent: str
    skills: tuple[SkillMetric, ...]


@dataclass(frozen=True)
class ProjectCard:
    title: str
    description: str
    stack: tuple[str, ...]
    github_url: str
    demo_url: str
    accent: str
    status: str = "production"


@dataclass(frozen=True)
class TechItem:
    name: str
    category: str
    accent: str
    icon: str


@dataclass(frozen=True)
class ProfileData:
    username: str
    name: str
    role: str
    subtitle: str
    focus: str
    location: str
    email: str
    portfolio: str
    linkedin: str
    twitter: str
    status: str
    social: tuple[SocialProfile, ...]
    skill_categories: tuple[SkillCategory, ...]
    projects: tuple[ProjectCard, ...]
    tech_stack: tuple[TechItem, ...]
    learning: tuple[str, ...]


def default_profile() -> ProfileData:
    username = "sankalp03326"
    email = "sankalp03326@example.com"
    portfolio = f"https://github.com/{username}"
    linkedin = "https://www.linkedin.com/in/sankalp-varshney8445"
    twitter = "https://x.com/sankalp03326"

    return ProfileData(
        username=username,
        name="Sankalp Varshney",
        role="Senior Software Engineer",
        subtitle="Cloud architecting, full-stack engineering, AI systems, and DevOps automation",
        focus=(
            "Building resilient product platforms with clean interfaces, secure backends, "
            "repeatable infrastructure, and data-aware automation."
        ),
        location="India",
        email=email,
        portfolio=portfolio,
        linkedin=linkedin,
        twitter=twitter,
        status="Available for senior engineering and cloud architecture work",
        social=(
            SocialProfile("GitHub", f"@{username}", f"https://github.com/{username}", "github", PALETTE.cyan),
            SocialProfile("LinkedIn", "Connect", linkedin, "linkedin", PALETTE.blue),
            SocialProfile("Portfolio", "Work archive", portfolio, "external", PALETTE.green),
            SocialProfile("Email", "Contact", f"mailto:{email}", "mail", PALETTE.amber),
            SocialProfile("Twitter/X", "Signal", twitter, "twitter", PALETTE.pink),
        ),
        skill_categories=(
            SkillCategory(
                "Frontend",
                "frontend",
                PALETTE.cyan,
                (
                    SkillMetric("React", 92, PALETTE.cyan, "react", "component architecture"),
                    SkillMetric("Next.js", 86, PALETTE.cyan, "next", "routing and rendering"),
                    SkillMetric("TypeScript", 88, PALETTE.cyan, "typescript", "type-safe product UI"),
                    SkillMetric("TailwindCSS", 82, PALETTE.cyan, "tailwind", "utility design systems"),
                ),
            ),
            SkillCategory(
                "Backend",
                "backend",
                PALETTE.purple,
                (
                    SkillMetric("Python", 90, PALETTE.purple, "python", "automation and services"),
                    SkillMetric("Node.js", 82, PALETTE.purple, "node", "API services"),
                    SkillMetric("PHP", 84, PALETTE.purple, "php", "CMS and integrations"),
                    SkillMetric("REST APIs", 88, PALETTE.purple, "api", "secure contracts"),
                ),
            ),
            SkillCategory(
                "Cloud",
                "cloud",
                PALETTE.green,
                (
                    SkillMetric("AWS", 82, PALETTE.green, "aws", "IAM, compute, storage"),
                    SkillMetric("Azure", 76, PALETTE.green, "azure", "identity and app hosting"),
                    SkillMetric("DigitalOcean", 88, PALETTE.green, "cloud", "droplets and managed DB"),
                    SkillMetric("S3/Spaces", 80, PALETTE.green, "storage", "object storage"),
                ),
            ),
            SkillCategory(
                "DevOps",
                "devops",
                PALETTE.amber,
                (
                    SkillMetric("Docker", 80, PALETTE.amber, "docker", "containers"),
                    SkillMetric("GitHub Actions", 86, PALETTE.amber, "github", "CI/CD"),
                    SkillMetric("Linux", 88, PALETTE.amber, "linux", "servers and shell"),
                    SkillMetric("Nginx", 82, PALETTE.amber, "nginx", "reverse proxy"),
                ),
            ),
            SkillCategory(
                "Database",
                "database",
                PALETTE.pink,
                (
                    SkillMetric("PostgreSQL", 82, PALETTE.pink, "database", "relational design"),
                    SkillMetric("MySQL", 84, PALETTE.pink, "database", "CMS and apps"),
                    SkillMetric("MongoDB", 68, PALETTE.pink, "database", "document stores"),
                    SkillMetric("Redis", 70, PALETTE.pink, "cache", "queues and cache"),
                ),
            ),
            SkillCategory(
                "AI",
                "ai",
                PALETTE.blue,
                (
                    SkillMetric("Data Science", 70, PALETTE.blue, "ai", "analysis workflows"),
                    SkillMetric("AI/ML", 66, PALETTE.blue, "brain", "model exploration"),
                    SkillMetric("Automation", 86, PALETTE.blue, "bolt", "workflow systems"),
                    SkillMetric("Python ML", 72, PALETTE.blue, "python", "notebooks and pipelines"),
                ),
            ),
        ),
        projects=(
            ProjectCard(
                "Energy Dive Ecosystem",
                "Premium digital media and market intelligence platform with dynamic sector hubs.",
                ("React", "Vite", "Tailwind", "PHP", "MySQL"),
                f"https://github.com/{username}",
                portfolio,
                PALETTE.cyan,
            ),
            ProjectCard(
                "Energ Members System",
                "JWT and OTP membership platform for secure premium content access.",
                ("React", "PHP", "REST", "Security"),
                f"https://github.com/{username}",
                portfolio,
                PALETTE.purple,
            ),
            ProjectCard(
                "Cloud Operations Toolkit",
                "Repeatable deployment, server hardening, and production automation workflows.",
                ("Linux", "Docker", "Nginx", "GitHub Actions"),
                f"https://github.com/{username}",
                portfolio,
                PALETTE.green,
            ),
            ProjectCard(
                "AI Research Console",
                "Notebook-friendly experimentation surface for data science and AI/ML workflows.",
                ("Python", "NumPy", "Pipelines", "Automation"),
                f"https://github.com/{username}",
                portfolio,
                PALETTE.amber,
                status="research",
            ),
        ),
        tech_stack=(
            TechItem("Python", "Programming", PALETTE.cyan, "python"),
            TechItem("TypeScript", "Programming", PALETTE.cyan, "typescript"),
            TechItem("JavaScript", "Programming", PALETTE.cyan, "javascript"),
            TechItem("PHP", "Programming", PALETTE.cyan, "php"),
            TechItem("React", "Frontend", PALETTE.purple, "react"),
            TechItem("Next.js", "Frontend", PALETTE.purple, "next"),
            TechItem("Node.js", "Backend", PALETTE.green, "node"),
            TechItem("Express", "Backend", PALETTE.green, "api"),
            TechItem("PostgreSQL", "Database", PALETTE.pink, "database"),
            TechItem("MySQL", "Database", PALETTE.pink, "database"),
            TechItem("MongoDB", "Database", PALETTE.pink, "database"),
            TechItem("Redis", "Database", PALETTE.pink, "cache"),
            TechItem("Docker", "DevOps", PALETTE.amber, "docker"),
            TechItem("Kubernetes", "DevOps", PALETTE.amber, "kubernetes"),
            TechItem("Terraform", "DevOps", PALETTE.amber, "terraform"),
            TechItem("GitHub Actions", "DevOps", PALETTE.amber, "github"),
            TechItem("Azure", "Cloud", PALETTE.blue, "azure"),
            TechItem("AWS", "Cloud", PALETTE.blue, "aws"),
            TechItem("Linux", "Infrastructure", PALETTE.green, "linux"),
            TechItem("Nginx", "Infrastructure", PALETTE.green, "nginx"),
            TechItem("TailwindCSS", "Frontend", PALETTE.purple, "tailwind"),
        ),
        learning=("Kubernetes", "Terraform", "AI/ML systems", "Data science pipelines"),
    )


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "item"


def stable_id(*parts: object) -> str:
    raw = "::".join(str(part) for part in parts)
    return "id-" + sha1(raw.encode("utf-8")).hexdigest()[:12]


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def fmt(value: float | int, digits: int = 1) -> str:
    if isinstance(value, int) or float(value).is_integer():
        return str(int(value))
    return f"{value:.{digits}f}"


def attrs(**values: object) -> str:
    rendered: list[str] = []
    for key, value in values.items():
        if value is None:
            continue
        name = key.rstrip("_").replace("_", "-")
        rendered.append(f'{name}="{escape(str(value), quote=True)}"')
    return " ".join(rendered)


def wrap_text(text: str, max_chars: int) -> list[str]:
    if max_chars <= 0:
        return [text]

    words = text.split()
    lines: list[str] = []
    current: list[str] = []

    for word in words:
        projected = " ".join((*current, word))
        if len(projected) <= max_chars:
            current.append(word)
            continue

        if current:
            lines.append(" ".join(current))
        current = [word]

    if current:
        lines.append(" ".join(current))

    return lines or [""]


def text_element(
    x: float,
    y: float,
    content: str,
    *,
    size: int = 14,
    fill: str = PALETTE.text,
    weight: int | str = 400,
    family: str = FONT_STACK,
    anchor: str = "start",
    opacity: float | None = None,
    extra: str = "",
) -> str:
    attr_text = attrs(
        x=f"{x:.1f}",
        y=f"{y:.1f}",
        font_family=family,
        font_size=size,
        font_weight=weight,
        text_anchor=anchor,
        fill=fill,
        opacity=opacity,
    )
    suffix = f" {extra}" if extra else ""
    return f"<text {attr_text}{suffix}>{escape(content)}</text>"


def multiline_text(
    x: float,
    y: float,
    lines: Sequence[str],
    *,
    size: int = 14,
    line_height: int = 20,
    fill: str = PALETTE.text,
    family: str = FONT_STACK,
    weight: int | str = 400,
    opacity: float | None = None,
) -> list[str]:
    return [
        text_element(
            x,
            y + index * line_height,
            line,
            size=size,
            fill=fill,
            family=family,
            weight=weight,
            opacity=opacity,
        )
        for index, line in enumerate(lines)
    ]


def rect(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    rx: float = 0,
    fill: str = "none",
    stroke: str | None = None,
    stroke_width: float | None = None,
    opacity: float | None = None,
    filter_: str | None = None,
    extra: str = "",
) -> str:
    attr_text = attrs(
        x=f"{x:.1f}",
        y=f"{y:.1f}",
        width=f"{width:.1f}",
        height=f"{height:.1f}",
        rx=f"{rx:.1f}" if rx else None,
        fill=fill,
        stroke=stroke,
        stroke_width=stroke_width,
        opacity=opacity,
        filter=filter_,
    )
    suffix = f" {extra}" if extra else ""
    return f"<rect {attr_text}{suffix} />"


def line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    stroke: str,
    stroke_width: float = 1,
    opacity: float | None = None,
    extra: str = "",
) -> str:
    attr_text = attrs(
        x1=f"{x1:.1f}",
        y1=f"{y1:.1f}",
        x2=f"{x2:.1f}",
        y2=f"{y2:.1f}",
        stroke=stroke,
        stroke_width=stroke_width,
        opacity=opacity,
    )
    suffix = f" {extra}" if extra else ""
    return f"<line {attr_text}{suffix} />"


def circle(
    cx: float,
    cy: float,
    r: float,
    *,
    fill: str,
    stroke: str | None = None,
    stroke_width: float | None = None,
    opacity: float | None = None,
    filter_: str | None = None,
    extra: str = "",
) -> str:
    attr_text = attrs(
        cx=f"{cx:.1f}",
        cy=f"{cy:.1f}",
        r=f"{r:.1f}",
        fill=fill,
        stroke=stroke,
        stroke_width=stroke_width,
        opacity=opacity,
        filter=filter_,
    )
    suffix = f" {extra}" if extra else ""
    return f"<circle {attr_text}{suffix} />"


def path(
    d: str,
    *,
    fill: str = "none",
    stroke: str | None = None,
    stroke_width: float | None = None,
    opacity: float | None = None,
    filter_: str | None = None,
    extra: str = "",
) -> str:
    attr_text = attrs(
        d=d,
        fill=fill,
        stroke=stroke,
        stroke_width=stroke_width,
        opacity=opacity,
        filter=filter_,
    )
    suffix = f" {extra}" if extra else ""
    return f"<path {attr_text}{suffix} />"


def animate(
    attribute: str,
    values: str | None = None,
    *,
    from_: str | float | None = None,
    to: str | float | None = None,
    begin: float = 0,
    dur: float = 1,
    repeat: str | None = None,
    fill: str | None = "freeze",
) -> str:
    attr_text = attrs(
        attributeName=attribute,
        values=values,
        **{"from": from_},
        to=to,
        begin=f"{begin:.3f}s",
        dur=f"{dur:.3f}s",
        repeatCount=repeat,
        fill=fill,
    )
    return f"<animate {attr_text} />"


def animate_transform(
    transform_type: str,
    values: str,
    *,
    begin: float = 0,
    dur: float = 1,
    repeat: str | None = None,
) -> str:
    attr_text = attrs(
        attributeName="transform",
        attributeType="XML",
        type=transform_type,
        values=values,
        begin=f"{begin:.3f}s",
        dur=f"{dur:.3f}s",
        repeatCount=repeat,
    )
    return f"<animateTransform {attr_text} />"


class SvgDocument:
    def __init__(
        self,
        *,
        width: int,
        height: int,
        title: str,
        description: str,
        id_prefix: str | None = None,
        palette: CyberpunkPalette = PALETTE,
    ) -> None:
        self.width = width
        self.height = height
        self.title = title
        self.description = description
        self.palette = palette
        self.id_prefix = id_prefix or stable_id(title, width, height)
        self.defs: list[str] = []
        self.body: list[str] = []

    def add_def(self, value: str) -> None:
        self.defs.append(value)

    def add(self, value: str) -> None:
        self.body.append(value)

    def extend(self, values: Iterable[str]) -> None:
        self.body.extend(values)

    def document(self) -> str:
        title_id = f"{self.id_prefix}-title"
        desc_id = f"{self.id_prefix}-desc"
        output = [
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" '
                f'height="{self.height}" viewBox="0 0 {self.width} {self.height}" '
                f'role="img" aria-labelledby="{title_id} {desc_id}" '
                'style="max-width:100%;height:auto;">'
            ),
            f'<title id="{title_id}">{escape(self.title)}</title>',
            f'<desc id="{desc_id}">{escape(self.description)}</desc>',
        ]
        if self.defs:
            output.append("<defs>")
            output.extend(self.defs)
            output.append("</defs>")
        output.extend(self.body)
        output.append("</svg>")
        return "\n".join(output) + "\n"


def cyberpunk_defs(prefix: str, palette: CyberpunkPalette = PALETTE) -> list[str]:
    return [
        (
            f'<linearGradient id="{prefix}-bg" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0%" stop-color="{palette.background}" />'
            f'<stop offset="48%" stop-color="{palette.background_2}" />'
            f'<stop offset="100%" stop-color="#120923" />'
            "</linearGradient>"
        ),
        (
            f'<linearGradient id="{prefix}-panel" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0%" stop-color="{palette.surface}" stop-opacity="0.96" />'
            f'<stop offset="100%" stop-color="#101A28" stop-opacity="0.80" />'
            "</linearGradient>"
        ),
        (
            f'<linearGradient id="{prefix}-neon" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0%" stop-color="{palette.cyan}" />'
            f'<stop offset="38%" stop-color="{palette.purple}" />'
            f'<stop offset="70%" stop-color="{palette.green}" />'
            f'<stop offset="100%" stop-color="{palette.pink}" />'
            "</linearGradient>"
        ),
        (
            f'<radialGradient id="{prefix}-orb" cx="50%" cy="50%" r="50%">'
            f'<stop offset="0%" stop-color="{palette.cyan}" stop-opacity="0.42" />'
            f'<stop offset="60%" stop-color="{palette.purple}" stop-opacity="0.16" />'
            f'<stop offset="100%" stop-color="{palette.background}" stop-opacity="0" />'
            "</radialGradient>"
        ),
        (
            f'<pattern id="{prefix}-grid" width="36" height="36" patternUnits="userSpaceOnUse">'
            f'<path d="M 36 0 L 0 0 0 36" fill="none" stroke="{palette.cyan}" '
            'stroke-opacity="0.08" stroke-width="1" />'
            "</pattern>"
        ),
        (
            f'<pattern id="{prefix}-scanlines" width="8" height="8" patternUnits="userSpaceOnUse">'
            f'<rect width="8" height="1" fill="{palette.text}" opacity="0.045" />'
            "</pattern>"
        ),
        (
            f'<filter id="{prefix}-glow" x="-60%" y="-60%" width="220%" height="220%">'
            '<feGaussianBlur stdDeviation="3.2" result="blur" />'
            '<feColorMatrix in="blur" type="matrix" values="0 0 0 0 0 0 0 0 0 0.96 0 0 0 0 1 0 0 0 0.62 0" result="neon" />'
            '<feMerge><feMergeNode in="neon" /><feMergeNode in="SourceGraphic" /></feMerge>'
            "</filter>"
        ),
        (
            f'<filter id="{prefix}-soft-glow" x="-40%" y="-40%" width="180%" height="180%">'
            '<feGaussianBlur stdDeviation="7" result="blur" />'
            '<feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>'
            "</filter>"
        ),
    ]


def background_layer(doc: SvgDocument) -> None:
    prefix = doc.id_prefix
    doc.extend(
        [
            rect(0, 0, doc.width, doc.height, fill=f"url(#{prefix}-bg)"),
            rect(0, 0, doc.width, doc.height, fill=f"url(#{prefix}-grid)"),
            rect(0, 0, doc.width, doc.height, fill=f"url(#{prefix}-scanlines)", opacity=0.7),
            circle(doc.width * 0.18, doc.height * 0.18, doc.width * 0.22, fill=f"url(#{prefix}-orb)", opacity=0.70),
            circle(doc.width * 0.78, doc.height * 0.24, doc.width * 0.18, fill=f"url(#{prefix}-orb)", opacity=0.45),
        ]
    )


def glass_panel(
    doc: SvgDocument,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    radius: float = 18,
    accent: str | None = None,
    opacity: float = 0.92,
    glow: bool = True,
) -> None:
    accent_color = accent or doc.palette.cyan
    filter_value = f"url(#{doc.id_prefix}-glow)" if glow else None
    doc.add(
        rect(
            x,
            y,
            width,
            height,
            rx=radius,
            fill=f"url(#{doc.id_prefix}-panel)",
            stroke=doc.palette.border,
            stroke_width=1,
            opacity=opacity,
        )
    )
    doc.add(
        rect(
            x + 1.5,
            y + 1.5,
            width - 3,
            height - 3,
            rx=max(0, radius - 2),
            fill="none",
            stroke=accent_color,
            stroke_width=1.1,
            opacity=0.22,
            filter_=filter_value,
        )
    )


def neon_rule(
    doc: SvgDocument,
    x: float,
    y: float,
    width: float,
    *,
    accent: str | None = None,
    delay: float = 0.0,
) -> None:
    accent_color = accent or doc.palette.cyan
    doc.add(
        line(
            x,
            y,
            x + width,
            y,
            stroke=accent_color,
            stroke_width=2,
            opacity=0.82,
            extra=f'filter="url(#{doc.id_prefix}-glow)"',
        )
    )
    doc.add(
        f'<rect x="{x:.1f}" y="{y - 2:.1f}" width="28" height="4" rx="2" fill="{accent_color}" opacity="0.9">'
        f'{animate("x", from_=f"{x:.1f}", to=f"{x + width - 28:.1f}", begin=delay, dur=4.8, repeat="indefinite", fill=None)}'
        "</rect>"
    )


ICON_PATHS: dict[str, str] = {
    "github": "M12 2 C6.48 2 2 6.59 2 12.26 C2 16.77 4.87 20.59 8.84 21.94 C9.34 22.04 9.52 21.72 9.52 21.45 L9.51 19.62 C6.73 20.24 6.14 18.24 6.14 18.24 C5.68 17.03 5.03 16.71 5.03 16.71 C4.12 16.07 5.10 16.08 5.10 16.08 C6.10 16.15 6.63 17.14 6.63 17.14 C7.52 18.70 8.97 18.25 9.54 17.99 C9.63 17.33 9.89 16.88 10.17 16.63 C7.95 16.37 5.62 15.49 5.62 11.55 C5.62 10.42 6.01 9.50 6.65 8.78 C6.55 8.52 6.20 7.47 6.75 6.05 C6.75 6.05 7.59 5.78 9.50 7.11 C10.30 6.88 11.15 6.77 12 6.76 C12.85 6.77 13.70 6.88 14.50 7.11 C16.41 5.78 17.25 6.05 17.25 6.05 C17.80 7.47 17.45 8.52 17.35 8.78 C17.99 9.50 18.38 10.42 18.38 11.55 C18.38 15.50 16.04 16.37 13.82 16.63 C14.18 16.95 14.50 17.58 14.50 18.54 L14.49 21.45 C14.49 21.72 14.67 22.05 15.18 21.94 C19.14 20.59 22 16.77 22 12.26 C22 6.59 17.52 2 12 2 Z",
    "linkedin": "M4.98 3.5 C4.98 4.88 3.86 6 2.5 6 C1.12 6 0 4.88 0 3.5 C0 2.12 1.12 1 2.5 1 C3.86 1 4.98 2.12 4.98 3.5 Z M0.43 8.05 H4.56 V23 H0.43 V8.05 Z M7.42 8.05 H11.38 V10.09 H11.44 C12.00 9.03 13.35 7.69 15.37 7.69 C19.57 7.69 20.35 10.46 20.35 14.06 V23 H16.22 V15.07 C16.22 13.18 16.19 10.75 13.59 10.75 C10.95 10.75 10.55 12.81 10.55 14.94 V23 H7.42 V8.05 Z",
    "mail": "M3 5 H21 C22.1 5 23 5.9 23 7 V18 C23 19.1 22.1 20 21 20 H3 C1.9 20 1 19.1 1 18 V7 C1 5.9 1.9 5 3 5 Z M3 7 L12 13 L21 7 M3 18 H21 V9.2 L12 15.1 L3 9.2 V18 Z",
    "external": "M5 5 H11 V7 H7 V17 H17 V13 H19 V19 H5 V5 Z M14 5 H21 V12 H19 V8.4 L11.7 15.7 L10.3 14.3 L17.6 7 H14 V5 Z",
    "twitter": "M22 5.9 C21.3 6.2 20.6 6.4 19.8 6.5 C20.6 6.0 21.2 5.2 21.5 4.3 C20.8 4.7 19.9 5.1 19.0 5.2 C18.3 4.4 17.3 4 16.2 4 C14.1 4 12.4 5.8 12.4 7.9 C12.4 8.2 12.4 8.5 12.5 8.8 C9.3 8.6 6.5 7.1 4.6 4.7 C4.3 5.3 4.1 6.0 4.1 6.7 C4.1 8.1 4.8 9.3 5.8 10.0 C5.2 10.0 4.6 9.8 4.1 9.5 V9.6 C4.1 11.5 5.4 13.0 7.1 13.4 C6.8 13.5 6.4 13.6 6.0 13.6 C5.7 13.6 5.5 13.5 5.2 13.5 C5.7 15.0 7.1 16.1 8.8 16.1 C7.5 17.1 5.8 17.7 4.0 17.7 C3.7 17.7 3.4 17.7 3.1 17.6 C4.8 18.7 6.9 19.4 9.1 19.4 C16.2 19.4 20.1 13.5 20.1 8.4 V7.9 C20.9 7.4 21.5 6.7 22 5.9 Z",
    "frontend": "M3 4 H21 V17 H13 V20 H17 V22 H7 V20 H11 V17 H3 V4 Z M5 6 V15 H19 V6 H5 Z",
    "backend": "M4 4 H20 V9 H4 V4 Z M6 6 V7 H8 V6 H6 Z M4 11 H20 V16 H4 V11 Z M6 13 V14 H8 V13 H6 Z M4 18 H20 V22 H4 V18 Z",
    "cloud": "M7.5 19 H18 C20.2 19 22 17.2 22 15 C22 12.9 20.4 11.2 18.4 11 C17.7 8.1 15.2 6 12.2 6 C9.7 6 7.5 7.5 6.6 9.7 C4 10.1 2 12.3 2 15 C2 17.2 3.8 19 6 19 H7.5 Z",
    "devops": "M12 2 L15 8 L21 9 L16.5 13.3 L17.6 20 L12 16.7 L6.4 20 L7.5 13.3 L3 9 L9 8 L12 2 Z",
    "database": "M12 3 C16.4 3 20 4.3 20 6 V18 C20 19.7 16.4 21 12 21 C7.6 21 4 19.7 4 18 V6 C4 4.3 7.6 3 12 3 Z M4 6 C4 7.7 7.6 9 12 9 C16.4 9 20 7.7 20 6 M4 12 C4 13.7 7.6 15 12 15 C16.4 15 20 13.7 20 12",
    "ai": "M12 2 C14.2 2 16 3.8 16 6 V7 H17 C19.2 7 21 8.8 21 11 V13 C21 15.2 19.2 17 17 17 H16 V18 C16 20.2 14.2 22 12 22 C9.8 22 8 20.2 8 18 V17 H7 C4.8 17 3 15.2 3 13 V11 C3 8.8 4.8 7 7 7 H8 V6 C8 3.8 9.8 2 12 2 Z M8 10 H16 M9 14 H15 M10 6 H14 M10 18 H14",
    "brain": "M8 4 C6 4 4.5 5.5 4.5 7.4 C3 8.1 2 9.6 2 11.4 C2 13 3 14.5 4.5 15.1 C4.6 17.8 6.7 20 9.5 20 H10 V4 H8 Z M16 4 C18 4 19.5 5.5 19.5 7.4 C21 8.1 22 9.6 22 11.4 C22 13 21 14.5 19.5 15.1 C19.4 17.8 17.3 20 14.5 20 H14 V4 H16 Z",
    "python": "M12 2 H16 C18 2 19 3 19 5 V9 C19 11 18 12 16 12 H9 C8 12 7 13 7 14 V16 H5 C3 16 2 15 2 13 V8 C2 6 3 5 5 5 H12 V4 H8 V2 H12 Z M12 22 H8 C6 22 5 21 5 19 V15 C5 13 6 12 8 12 H15 C16 12 17 11 17 10 V8 H19 C21 8 22 9 22 11 V16 C22 18 21 19 19 19 H12 V20 H16 V22 H12 Z",
    "typescript": "M3 3 H21 V21 H3 V3 Z M7 8 H16 V10 H12.6 V18 H10.4 V10 H7 V8 Z M17.2 18 C16.2 18 15.4 17.7 14.8 17.2 L15.8 15.7 C16.2 16.1 16.8 16.4 17.4 16.4 C18 16.4 18.3 16.1 18.3 15.8 C18.3 15.4 18.0 15.2 17.2 14.9 C16.1 14.5 15 14.0 15 12.7 C15 11.4 16.1 10.5 17.6 10.5 C18.4 10.5 19.2 10.8 19.8 11.3 L18.9 12.8 C18.4 12.4 17.9 12.2 17.4 12.2 C16.9 12.2 16.6 12.4 16.6 12.8 C16.6 13.2 17.0 13.4 17.8 13.7 C18.9 14.1 20 14.7 20 15.9 C20 17.1 19.1 18 17.2 18 Z",
    "react": "M12 10.2 C13 10.2 13.8 11 13.8 12 C13.8 13 13 13.8 12 13.8 C11 13.8 10.2 13 10.2 12 C10.2 11 11 10.2 12 10.2 Z M12 5 C16.5 5 20.2 8.1 20.2 12 C20.2 15.9 16.5 19 12 19 C7.5 19 3.8 15.9 3.8 12 C3.8 8.1 7.5 5 12 5 Z M4.5 8 C6.7 4.1 11.2 2.5 14.6 4.5 C18 6.5 19 11.1 16.8 15 C14.6 18.9 10.1 20.5 6.7 18.5 C3.3 16.5 2.3 11.9 4.5 8 Z M19.5 8 C21.7 11.9 20.7 16.5 17.3 18.5 C13.9 20.5 9.4 18.9 7.2 15 C5 11.1 6 6.5 9.4 4.5 C12.8 2.5 17.3 4.1 19.5 8 Z",
    "next": "M12 2 C17.5 2 22 6.5 22 12 C22 17.5 17.5 22 12 22 C6.5 22 2 17.5 2 12 C2 6.5 6.5 2 12 2 Z M8 8 V16 H10 V11.4 L16 19 C16.7 18.6 17.3 18.1 17.8 17.5 L11.6 8 H8 Z M15 8 V14 H17 V8 H15 Z",
    "node": "M12 2 L21 7 V17 L12 22 L3 17 V7 L12 2 Z M12 5 L6 8.3 V15.7 L12 19 L18 15.7 V8.3 L12 5 Z",
    "docker": "M4 13 H22 C21.6 16.5 19.2 19 15.6 19 H9 C5.7 19 3.3 17 2 14 C2.7 13.5 3.4 13.2 4 13 Z M5 8 H8 V11 H5 V8 Z M9 8 H12 V11 H9 V8 Z M13 8 H16 V11 H13 V8 Z M9 4 H12 V7 H9 V4 Z M13 4 H16 V7 H13 V4 Z M17 8 H20 V11 H17 V8 Z",
    "kubernetes": "M12 2 L20.7 7 V17 L12 22 L3.3 17 V7 L12 2 Z M12 6.2 L14.7 9 L18.5 9.5 L16.4 12.7 L17.1 16.5 L13.5 15 L10.5 17.2 L10.2 13.4 L7.1 11.2 L10.5 10 L12 6.2 Z",
    "terraform": "M4 3 L10 6.5 V13.5 L4 10 V3 Z M11 7 L17 10.5 V17.5 L11 14 V7 Z M18 10.8 L22 8.5 V15.5 L18 17.8 V10.8 Z M4 11.2 L10 14.7 V21.7 L4 18.2 V11.2 Z",
    "aws": "M5 15 C8.5 17 15.5 17 19 15 M8 13 L10 6 H14 L16 13 M8.7 11 H15.3 M4 18 C9 22 16 22 21 18 M3 8 C4 5 7 3 10 3 H14 C17 3 20 5 21 8",
    "azure": "M13 3 L5 20 H12 L13.5 16 H9.5 L14.5 6.5 L13 3 Z M15 7 L21 20 H13 L16.5 16 L15 7 Z",
    "linux": "M12 2 C14 2 15.5 4 15.2 6.5 C16.6 8.2 17.4 10.8 17.4 13.2 L21 19 L17 21 L14.8 17.8 H9.2 L7 21 L3 19 L6.6 13.2 C6.6 10.8 7.4 8.2 8.8 6.5 C8.5 4 10 2 12 2 Z",
    "nginx": "M12 2 L20.7 7 V17 L12 22 L3.3 17 V7 L12 2 Z M8 8 H10.2 L14 14 V8 H16 V16 H13.8 L10 10 V16 H8 V8 Z",
    "tailwind": "M7.5 10 C8.4 6.8 10.4 5.2 13.5 5.2 C15.8 5.2 17.4 6.4 18.4 8.8 C17.4 8.1 16.3 7.8 15.2 7.8 C13.6 7.8 12.5 8.5 11.8 9.9 C10.9 11.7 9.4 12.6 7.4 12.6 C5.9 12.6 4.6 12.2 3.5 11.3 C4.5 12.9 5.9 13.7 7.8 13.7 C9.5 13.7 10.8 13 11.7 11.6 C12.6 10 13.9 9.2 15.6 9.2 C17.5 9.2 19 10 20.5 11.7 C19.7 14.8 17.7 16.4 14.6 16.4 C12.3 16.4 10.7 15.2 9.7 12.8 C10.7 13.5 11.8 13.8 12.9 13.8 C14.5 13.8 15.6 13.1 16.3 11.7 C17.2 9.9 18.7 9 20.7 9 C22.1 9 23.4 9.4 24.5 10.3 C23.5 8.7 22.1 7.9 20.2 7.9 C18.5 7.9 17.2 8.6 16.3 10 C15.4 11.6 14.1 12.4 12.4 12.4 C10.5 12.4 9 11.6 7.5 10 Z",
    "api": "M4 7 H10 V9 H6 V15 H10 V17 H4 V7 Z M14 7 H20 V17 H14 V15 H18 V9 H14 V7 Z M10 14 L14 10 M14 14 L10 10",
    "cache": "M4 6 C4 4.3 7.6 3 12 3 C16.4 3 20 4.3 20 6 C20 7.7 16.4 9 12 9 C7.6 9 4 7.7 4 6 Z M4 10 C4 11.7 7.6 13 12 13 C16.4 13 20 11.7 20 10 V14 C20 15.7 16.4 17 12 17 C7.6 17 4 15.7 4 14 V10 Z M4 18 C5.5 20 8.5 21 12 21 C15.5 21 18.5 20 20 18",
    "bolt": "M13 2 L4 14 H11 L9 22 L20 9 H13 L13 2 Z",
    "storage": "M4 5 H20 V9 H4 V5 Z M4 10 H20 V14 H4 V10 Z M4 15 H20 V19 H4 V15 Z M6 6.5 H8 M6 11.5 H8 M6 16.5 H8",
}


def icon(name: str, x: float, y: float, size: float, color: str, *, opacity: float = 1.0) -> str:
    icon_name = name if name in ICON_PATHS else "bolt"
    scale = size / 24
    return (
        f'<g transform="translate({x:.1f} {y:.1f}) scale({scale:.4f})" '
        f'fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round" opacity="{opacity:.2f}">'
        f'<path d="{ICON_PATHS[icon_name]}" />'
        "</g>"
    )


def solid_icon(name: str, x: float, y: float, size: float, color: str, *, opacity: float = 1.0) -> str:
    icon_name = name if name in ICON_PATHS else "bolt"
    scale = size / 24
    return (
        f'<g transform="translate({x:.1f} {y:.1f}) scale({scale:.4f})" '
        f'fill="{color}" opacity="{opacity:.2f}">'
        f'<path d="{ICON_PATHS[icon_name]}" />'
        "</g>"
    )


def progress_bar(
    doc: SvgDocument,
    x: float,
    y: float,
    width: float,
    height: float,
    percent: float,
    *,
    accent: str,
    delay: float = 0.0,
    label: str | None = None,
) -> None:
    value = clamp(percent, 0, 100)
    target = width * (value / 100)
    clip_id = f"{doc.id_prefix}-bar-{stable_id(x, y, width, percent)}"
    doc.add(
        rect(
            x,
            y,
            width,
            height,
            rx=height / 2,
            fill=doc.palette.surface_2,
            stroke=doc.palette.border,
            stroke_width=1,
        )
    )
    doc.add(
        f'<clipPath id="{clip_id}">'
        f'<rect x="{x:.1f}" y="{y:.1f}" width="0" height="{height:.1f}" '
        f'rx="{height / 2:.1f}" fill="#fff">'
        f'{animate("width", from_=0, to=f"{target:.1f}", begin=delay, dur=1.2)}'
        "</rect></clipPath>"
    )
    doc.add(
        rect(
            x,
            y,
            width,
            height,
            rx=height / 2,
            fill=accent,
            opacity=0.92,
            filter_=f"url(#{doc.id_prefix}-glow)",
            extra=f'clip-path="url(#{clip_id})"',
        )
    )
    if label:
        doc.add(text_element(x + width + 12, y + height - 2, label, size=11, fill=doc.palette.muted, family=MONO_FONT_STACK))


def metric_card(
    doc: SvgDocument,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    label: str,
    value: str,
    accent: str,
    icon_name: str,
    delay: float = 0.0,
) -> None:
    glass_panel(doc, x, y, width, height, radius=16, accent=accent, glow=False)
    doc.add(circle(x + 30, y + 32, 18, fill=accent, opacity=0.08))
    doc.add(icon(icon_name, x + 18, y + 20, 24, accent, opacity=0.95))
    doc.add(
        f'<g opacity="0">{animate("opacity", from_=0, to=1, begin=delay, dur=0.6)}'
        f'{text_element(x + 60, y + 34, label.upper(), size=10, fill=doc.palette.muted, weight=700, family=MONO_FONT_STACK)}'
        f'{text_element(x + 60, y + 66, value, size=25, fill=doc.palette.text, weight=800, family=MONO_FONT_STACK)}'
        "</g>"
    )
    neon_rule(doc, x + 18, y + height - 16, width - 36, accent=accent, delay=delay)


def pill(
    doc: SvgDocument,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    label: str,
    accent: str,
    icon_name: str | None = None,
    delay: float = 0.0,
) -> None:
    content = [
        rect(x, y, width, height, rx=height / 2, fill=doc.palette.surface_2, stroke=accent, stroke_width=1, opacity=0.86),
    ]
    text_x = x + 18
    if icon_name:
        content.append(icon(icon_name, x + 12, y + 9, 18, accent, opacity=0.92))
        text_x += 24
    content.append(text_element(text_x, y + height / 2 + 4, label, size=12, fill=doc.palette.text, weight=650, family=MONO_FONT_STACK))
    doc.add(f'<g opacity="0">{animate("opacity", from_=0, to=1, begin=delay, dur=0.45)}{"".join(content)}</g>')


def section_header(
    doc: SvgDocument,
    x: float,
    y: float,
    *,
    kicker: str,
    title: str,
    accent: str | None = None,
) -> None:
    accent_color = accent or doc.palette.cyan
    doc.add(text_element(x, y, kicker.upper(), size=11, fill=accent_color, weight=800, family=MONO_FONT_STACK))
    doc.add(text_element(x, y + 32, title, size=27, fill=doc.palette.text, weight=850, family=FONT_STACK))
    neon_rule(doc, x, y + 48, 176, accent=accent_color, delay=0.2)


def month_key(day: date) -> str:
    return day.strftime("%Y-%m")


def pretty_int(value: int | float) -> str:
    numeric = int(value)
    if abs(numeric) >= 1_000_000:
        return f"{numeric / 1_000_000:.1f}M"
    if abs(numeric) >= 1_000:
        return f"{numeric / 1_000:.1f}K"
    return str(numeric)


def grid_positions(
    count: int,
    *,
    columns: int,
    x: float,
    y: float,
    card_width: float,
    card_height: float,
    gap_x: float,
    gap_y: float,
) -> list[tuple[float, float]]:
    positions: list[tuple[float, float]] = []
    for index in range(count):
        row = index // columns
        column = index % columns
        positions.append((x + column * (card_width + gap_x), y + row * (card_height + gap_y)))
    return positions


def document_height_for_grid(
    item_count: int,
    *,
    columns: int,
    top: int,
    card_height: int,
    gap_y: int,
    bottom: int,
) -> int:
    rows = ceil(item_count / columns)
    return top + rows * card_height + max(0, rows - 1) * gap_y + bottom
