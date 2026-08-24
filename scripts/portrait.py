from pathlib import Path

import cv2
import numpy as np


# =========================================================
# Configuration
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

SOURCE = ROOT / "assets" / "portrait" / "source.jpg"
OUTPUT = ROOT / "assets" / "portrait" / "portrait.txt"

# Width of the final ASCII portrait
COLUMNS = 90

# Dark -> bright.
# The first character is a space so bright/white areas disappear.
RAMP = " .:-=+*#%@"

# Monospace characters are taller than they are wide.
CHAR_ASPECT = 0.48


# =========================================================
# Load image
# =========================================================

def load_image(path: Path) -> np.ndarray:
    print("Loading image...")

    image = cv2.imread(str(path))

    if image is None:
        raise RuntimeError(f"Could not read image: {path}")

    return image


# =========================================================
# Prepare image
# =========================================================

def prepare_image(image: np.ndarray) -> np.ndarray:
    print("Preparing image...")

    # -----------------------------------------------------
    # Detect the original white background BEFORE applying
    # any contrast processing.
    # -----------------------------------------------------

    # OpenCV loads images as BGR.
    b, g, r = cv2.split(image)

    background_mask = (
        (b > 245) &
        (g > 245) &
        (r > 245)
    )

    # -----------------------------------------------------
    # Convert to grayscale
    # -----------------------------------------------------

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Smooth small noise while preserving edges.
    gray = cv2.bilateralFilter(
        gray,
        d=9,
        sigmaColor=75,
        sigmaSpace=75
    )

    # -----------------------------------------------------
    # Local contrast enhancement
    # -----------------------------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=3.0,
        tileGridSize=(8, 8)
    )

    gray = clahe.apply(gray)

    # -----------------------------------------------------
    # Darkening curve
    # -----------------------------------------------------

    normalized = gray.astype(np.float32) / 255.0

    normalized = np.power(
        normalized,
        1.7
    )

    gray = np.clip(
        normalized * 255,
        0,
        255
    ).astype(np.uint8)

    # -----------------------------------------------------
    # Restore the original white background.
    #
    # This prevents the contrast processing from turning
    # the white background into @ characters.
    # -----------------------------------------------------

    gray[background_mask] = 255

    return gray


# =========================================================
# Crop
# =========================================================

def crop_image(gray: np.ndarray) -> np.ndarray:
    print("Cropping image...")

    height, width = gray.shape

    # Your photo already has a good composition.
    # We remove only a small amount of empty border.
    left = int(width * 0.03)
    right = int(width * 0.97)

    top = int(height * 0.02)
    bottom = int(height * 0.98)

    return gray[top:bottom, left:right]


# =========================================================
# Resize
# =========================================================

def resize_for_ascii(gray: np.ndarray) -> np.ndarray:
    height, width = gray.shape

    rows = round(
        COLUMNS
        * (height / width)
        * CHAR_ASPECT
    )

    print(f"ASCII dimensions: {COLUMNS} × {rows}")

    resized = cv2.resize(
        gray,
        (COLUMNS, rows),
        interpolation=cv2.INTER_AREA
    )

    return resized


# =========================================================
# Convert pixels → ASCII
# =========================================================

def to_ascii(gray: np.ndarray) -> str:
    print("Converting pixels to ASCII...")

    output = []

    maximum = len(RAMP) - 1

    for row in gray:

        line = []

        for pixel in row:

            # Pure/light background becomes completely empty.
            if pixel >= 245:
                line.append(" ")
                continue

            # Dark pixels become dense ASCII characters.
            index = int(
                pixel / 255 * maximum
            )

            line.append(RAMP[index])

        output.append("".join(line).rstrip())

    return "\n".join(output)


# =========================================================
# Main
# =========================================================

def main():

    if not SOURCE.exists():

        raise FileNotFoundError(
            f"Source image not found:\n{SOURCE}"
        )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    image = load_image(SOURCE)

    gray = prepare_image(image)

    gray = crop_image(gray)

    resized = resize_for_ascii(gray)

    ascii_art = to_ascii(resized)

    OUTPUT.write_text(
        ascii_art,
        encoding="utf-8"
    )

    print()
    print("=" * 60)
    print("ASCII PORTRAIT")
    print("=" * 60)
    print()

    print(ascii_art)

    print()
    print("=" * 60)
    print(f"Saved to: {OUTPUT}")
    print("=" * 60)


if __name__ == "__main__":
    main()