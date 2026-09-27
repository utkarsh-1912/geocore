"""Regenerate the Windows (NSIS) installer bitmaps from the GeoCore logo.

Run from electron-app/:  python installer/generate_assets.py
Requires Pillow. Output is committed, so this only needs re-running when the
branding changes. NSIS needs uncompressed 24-bit BMPs at these exact sizes.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
LOGO = HERE.parent / "src" / "assets" / "logoIcon.png"

# Brand tokens (see src/index.css)
DEEP = (22, 32, 27)          # --color-text-main (light) / near-black green
SECONDARY = (45, 71, 62)     # --color-secondary
PRIMARY = (95, 132, 69)      # --color-primary
PRIMARY_LIGHT = (177, 208, 130)
PAGE_BG = (245, 247, 243)    # --color-background (light); keep in sync with installer.nsh

SIDEBAR_SIZE = (164, 314)
HEADER_SIZE = (150, 57)


def font(size, bold=False):
    names = ["segoeuib.ttf", "seguisb.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def logo(size):
    img = Image.open(LOGO).convert("RGBA")
    return img.resize((size, size), Image.LANCZOS)


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def centred_text(draw, width, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text(((width - w) / 2, y), text, font=fnt, fill=fill)


def sidebar():
    w, h = SIDEBAR_SIZE
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)

    # Vertical gradient: brand secondary -> deep green.
    for y in range(h):
        draw.line([(0, y), (w, y)], fill=lerp(SECONDARY, DEEP, y / (h - 1)))

    # Soil strata along the bottom — a quiet nod to borehole logs.
    strata = [(0.70, 0.10), (0.78, 0.16), (0.86, 0.22), (0.93, 0.30)]
    for i, (top, alpha) in enumerate(strata):
        y0 = int(h * top)
        pts = [(x, y0 + 4 * ((x // 20 + i) % 2)) for x in range(0, w + 20, 20)]
        colour = lerp(DEEP, PRIMARY, alpha)
        draw.polygon(pts + [(w, h), (0, h)], fill=colour)

    mark = logo(76)
    img.paste(mark, ((w - 76) // 2, 58), mark)

    centred_text(draw, w, 146, "GeoCore", font(22, bold=True), (255, 255, 255))
    centred_text(draw, w, 176, "Geotechnical", font(11), PRIMARY_LIGHT)
    centred_text(draw, w, 191, "engineering suite", font(11), PRIMARY_LIGHT)
    return img


def header():
    w, h = HEADER_SIZE
    img = Image.new("RGB", (w, h), PAGE_BG)
    draw = ImageDraw.Draw(img)
    mark = logo(34)
    x = w - 34 - 10
    img.paste(mark, (x, (h - 34) // 2), mark)
    fnt = font(15, bold=True)
    tw = draw.textlength("GeoCore", font=fnt)
    draw.text((x - 8 - tw, (h - 20) // 2), "GeoCore", font=fnt, fill=DEEP)
    return img


if __name__ == "__main__":
    side = sidebar()
    side.save(HERE / "installerSidebar.bmp")
    side.save(HERE / "uninstallerSidebar.bmp")
    header().save(HERE / "installerHeader.bmp")
    print("Wrote installer bitmaps to", HERE)
