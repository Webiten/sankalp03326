from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageOps


DEFAULT_DENSITY_RAMP = (
    "$@B%8&WM#*oahkbdpqwmZO0QLCJUYX"
    "zcvunxrjft/\\|()1{}[]?-_+~<>"
    "i!lI;:,\"^`'. "
)


@dataclass(frozen=True)
class AsciiConfig:
    width: int = 100
    brightness: float = 1.04
    contrast: float = 1.18
    gamma: float = 0.92
    invert: bool = False
    character_aspect_ratio: float = 0.50
    density_ramp: str = DEFAULT_DENSITY_RAMP
    min_height: int = 1

    def validate(self) -> None:
        if self.width < 8:
            raise ValueError("ASCII width must be at least 8 characters")
        if self.brightness <= 0:
            raise ValueError("Brightness must be greater than zero")
        if self.contrast <= 0:
            raise ValueError("Contrast must be greater than zero")
        if self.gamma <= 0:
            raise ValueError("Gamma must be greater than zero")
        if self.character_aspect_ratio <= 0:
            raise ValueError("Character aspect ratio must be greater than zero")
        if len(self.density_ramp) < 2:
            raise ValueError("Density ramp must contain at least two characters")
        if self.min_height < 1:
            raise ValueError("Minimum height must be at least one row")


def _target_height(image: Image.Image, config: AsciiConfig) -> int:
    source_width, source_height = image.size
    scaled_height = (source_height / source_width) * config.width
    return max(config.min_height, int(round(scaled_height * config.character_aspect_ratio)))


def _apply_gamma(image: Image.Image, gamma: float) -> Image.Image:
    lookup = [
        min(255, max(0, int(round(((value / 255.0) ** gamma) * 255))))
        for value in range(256)
    ]
    return image.point(lookup)


def prepare_image(image: Image.Image, config: AsciiConfig) -> Image.Image:
    config.validate()

    normalized = ImageOps.exif_transpose(image).convert("L")
    normalized = normalized.resize(
        (config.width, _target_height(normalized, config)),
        Image.Resampling.LANCZOS,
    )
    normalized = ImageEnhance.Brightness(normalized).enhance(config.brightness)
    normalized = ImageEnhance.Contrast(normalized).enhance(config.contrast)
    return _apply_gamma(normalized, config.gamma)


def image_to_ascii(image: Image.Image, config: AsciiConfig | None = None) -> list[str]:
    config = config or AsciiConfig()
    prepared = prepare_image(image, config)
    pixels = np.asarray(prepared, dtype=np.uint16)

    if config.invert:
        pixels = 255 - pixels

    ramp = np.asarray(tuple(config.density_ramp))
    indices = (pixels * (len(ramp) - 1) // 255).astype(np.int16)
    return ["".join(ramp[row]) for row in indices]


def render_image(path: Path, config: AsciiConfig | None = None) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    with Image.open(path) as image:
        return image_to_ascii(image, config)


def write_preview(rows: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
