from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


@dataclass(frozen=True)
class PhotoPrepConfig:
    source: Path = Path("assets/portrait.jpg")
    output: Path = Path("assets/source-prepped.png")
    remove_background: bool = True
    background_color: tuple[int, int, int] = (255, 255, 255)
    autocontrast_cutoff: float = 1.0
    brightness: float = 1.03
    contrast: float = 1.16
    sharpness: float = 1.08


def _remove_background(source: Path) -> Image.Image:
    try:
        from rembg import remove
    except ImportError as exc:
        raise RuntimeError(
            "rembg is required for background removal. "
            "Install dependencies with `pip install -r requirements.txt`."
        ) from exc

    output_bytes = remove(source.read_bytes())
    return Image.open(BytesIO(output_bytes)).convert("RGBA")


def _flatten_on_background(
    image: Image.Image,
    background_color: tuple[int, int, int],
) -> Image.Image:
    rgba = image.convert("RGBA")
    background = Image.new("RGBA", rgba.size, (*background_color, 255))
    background.alpha_composite(rgba)
    return background.convert("RGB")


def preprocess_photo(config: PhotoPrepConfig | None = None) -> Path:
    config = config or PhotoPrepConfig()
    if not config.source.exists():
        raise FileNotFoundError(f"Portrait not found: {config.source}")

    if config.remove_background:
        image = _remove_background(config.source)
    else:
        image = Image.open(config.source)

    image = ImageOps.exif_transpose(image)
    flattened = _flatten_on_background(image, config.background_color)
    grayscale = ImageOps.autocontrast(
        flattened.convert("L"),
        cutoff=config.autocontrast_cutoff,
    )
    grayscale = ImageEnhance.Brightness(grayscale).enhance(config.brightness)
    grayscale = ImageEnhance.Contrast(grayscale).enhance(config.contrast)
    grayscale = ImageEnhance.Sharpness(grayscale).enhance(config.sharpness)

    config.output.parent.mkdir(parents=True, exist_ok=True)
    grayscale.save(config.output)
    return config.output


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Prepare a portrait for ASCII rendering.")
    parser.add_argument("--input", type=Path, default=Path("assets/portrait.jpg"))
    parser.add_argument("--output", type=Path, default=Path("assets/source-prepped.png"))
    parser.add_argument(
        "--no-rembg",
        action="store_true",
        help="Skip background removal and only normalize contrast.",
    )
    args = parser.parse_args()

    output = preprocess_photo(
        PhotoPrepConfig(
            source=args.input,
            output=args.output,
            remove_background=not args.no_rembg,
        )
    )
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
