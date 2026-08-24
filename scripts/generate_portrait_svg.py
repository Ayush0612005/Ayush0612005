from pathlib import Path
from xml.sax.saxutils import escape


# =========================================================
# Paths
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "assets" / "portrait" / "portrait.txt"
OUTPUT = ROOT / "assets" / "portrait" / "portrait.svg"


# =========================================================
# Portrait geometry
# =========================================================

# Large enough for a clear local preview and GitHub display.
FONT_SIZE = 16

# The ASCII portrait was generated assuming a 0.600em
# monospace character advance.
CHAR_W = FONT_SIZE * 0.600

# Keep rows compact so the portrait doesn't become too tall.
LINE_H = FONT_SIZE

# Final SVG display width.
DISPLAY_WIDTH = 700

# Space around the portrait.
PADDING_X = 30
PADDING_Y = 20


# =========================================================
# Animation
# =========================================================

# Delay between the beginning of consecutive rows.
ROW_DELAY = 0.09

# Time for one row to reveal itself.
ROW_DURATION = 0.55


# =========================================================
# Appearance
# =========================================================

# Dark enough to see clearly on a white browser background.
# We will later switch this for the GitHub dark theme.
TEXT_COLOR = "#c9d1d9"

# Fallback fonts for local testing.
FONT_FAMILY = (
    '"DejaVu Sans Mono", '
    '"Liberation Mono", '
    'monospace'
)


# =========================================================
# Read ASCII portrait
# =========================================================

def read_portrait() -> list[str]:
    """Read the generated ASCII portrait."""

    if not INPUT.exists():
        raise FileNotFoundError(
            f"""
Portrait file not found:

{INPUT}

Run:

python scripts\\portrait.py
"""
        )

    return INPUT.read_text(
        encoding="utf-8"
    ).splitlines()


# =========================================================
# Generate SVG
# =========================================================

def generate_svg(rows: list[str]) -> str:
    """Convert the ASCII portrait into an animated SVG."""

    if not rows:
        raise ValueError(
            "portrait.txt is empty."
        )

    # -----------------------------------------------------
    # Determine portrait dimensions
    # -----------------------------------------------------

    max_columns = max(
        len(row)
        for row in rows
    )

    row_count = len(rows)

    portrait_width = (
        max_columns * CHAR_W
    )

    portrait_height = (
        row_count * LINE_H
    )

    canvas_width = (
        portrait_width
        + PADDING_X * 2
    )

    canvas_height = (
        portrait_height
        + PADDING_Y * 2
    )

    svg = []

    # -----------------------------------------------------
    # SVG header
    # -----------------------------------------------------

    svg.append(
        f'''<?xml version="1.0" encoding="UTF-8"?>
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{DISPLAY_WIDTH}"
    viewBox="0 0 {canvas_width:.2f} {canvas_height:.2f}"
    role="img"
    aria-label="Animated ASCII portrait of Ayush Kulshreshtha"
>
'''
    )

    # -----------------------------------------------------
    # Font
    # -----------------------------------------------------

    svg.append(
        f'''    <style>
        .portrait {{
            font-family: {FONT_FAMILY};
            font-size: {FONT_SIZE}px;
            font-weight: 400;
            letter-spacing: 0;
            white-space: pre;
        }}
    </style>

'''
    )

    # -----------------------------------------------------
    # Clip paths
    #
    # Each row gets its own animated clipping rectangle.
    # This creates the typing/wipe effect.
    # -----------------------------------------------------

    svg.append(
        "    <defs>\n"
    )

    for i, row in enumerate(rows):

        row_width = max(
            CHAR_W,
            len(row) * CHAR_W
        )

        text_y = (
            PADDING_Y
            + (i + 1) * LINE_H
        )

        clip_y = (
            text_y
            - FONT_SIZE
            - 2
        )

        clip_height = (
            LINE_H
            + FONT_SIZE * 0.4
        )

        start_time = (
            i * ROW_DELAY
        )

        svg.append(
            f'''        <clipPath id="clip-{i}">
            <rect
                x="{PADDING_X:.2f}"
                y="{clip_y:.2f}"
                width="0"
                height="{clip_height:.2f}"
            >
                <animate
                    attributeName="width"
                    from="0"
                    to="{row_width:.2f}"
                    begin="{start_time:.2f}s"
                    dur="{ROW_DURATION:.2f}s"
                    fill="freeze"
                />
            </rect>
        </clipPath>
'''
        )

    svg.append(
        "    </defs>\n\n"
    )

    # -----------------------------------------------------
    # Portrait
    # -----------------------------------------------------

    svg.append(
        f'''    <g
        class="portrait"
        fill="{TEXT_COLOR}"
    >
'''
    )

    for i, row in enumerate(rows):

        text_y = (
            PADDING_Y
            + (i + 1) * LINE_H
        )

        svg.append(
            f'''        <text
            x="{PADDING_X:.2f}"
            y="{text_y:.2f}"
            clip-path="url(#clip-{i})"
        >{escape(row)}</text>
'''
        )

    svg.append(
        "    </g>\n\n"
    )

    # -----------------------------------------------------
    # Typing cursor
    #
    # The small block follows the right edge of each row
    # while the row is being revealed.
    # -----------------------------------------------------

    svg.append(
        f'''    <g
        fill="{TEXT_COLOR}"
        pointer-events="none"
    >
'''
    )

    for i, row in enumerate(rows):

        row_width = max(
            CHAR_W,
            len(row) * CHAR_W
        )

        y = (
            PADDING_Y
            + i * LINE_H
        )

        start_time = (
            i * ROW_DELAY
        )

        svg.append(
            f'''        <rect
            x="{PADDING_X:.2f}"
            y="{y:.2f}"
            width="2"
            height="{LINE_H:.9f}"
            opacity="0"
        >
            <animate
                attributeName="x"
                from="{PADDING_X:.2f}"
                to="{PADDING_X + row_width:.2f}"
                begin="{start_time:.2f}s"
                dur="{ROW_DURATION:.2f}s"
                fill="freeze"
            />

            <animate
                attributeName="opacity"
                values="0;1;1;0"
                keyTimes="0;0.05;0.90;1"
                begin="{start_time:.2f}s"
                dur="{ROW_DURATION:.2f}s"
                fill="freeze"
            />
        </rect>
'''
        )

    svg.append(
        "    </g>\n"
    )

    # -----------------------------------------------------
    # Close SVG
    # -----------------------------------------------------

    svg.append(
        "</svg>\n"
    )

    return "".join(svg)


# =========================================================
# Main
# =========================================================

def main():

    rows = read_portrait()

    svg = generate_svg(rows)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print("=" * 60)
    print("PORTRAIT SVG GENERATED")
    print("=" * 60)
    print()
    print(f"Rows:           {len(rows)}")
    print(f"Characters:     {max(map(len, rows))}")
    print(f"Font size:      {FONT_SIZE}px")
    print(f"Character width:{CHAR_W:.2f}px")
    print(f"Display width:  {DISPLAY_WIDTH}px")
    print(f"Row delay:      {ROW_DELAY}s")
    print(f"Row duration:   {ROW_DURATION}s")
    print()
    print("Output:")
    print(OUTPUT)
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()