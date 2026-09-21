#!/usr/bin/env python3
"""
Generates the animated terminal-style GitHub profile banner (dark.svg / light.svg)
by converting a headshot photo into ASCII art and pairing it with a live
"terminal readout" info panel.

Usage:
    python3 ascii_to_svg.py --photo photo.png --out-dir assets
"""

import argparse
from PIL import Image

RAMP = " .:-=+*#%@"

# ---- content of the terminal info panel -------------------------------
LINES = [
    ("Subject",      "Prajwal Kuderu Suresh (\"Bunny\")"),
    ("Role",         "SOC Analyst (L1) :: Threat Detection & Response"),
    ("Origin",       "Bengaluru, IN -> Milton Keynes, UK"),
    ("Education",    "MSc Cyber Security, Univ. of Hertfordshire"),
    ("Dissertation", "AI-Powered Ransomware Detection"),
    ("Status",       "[x] Job Hunting  [x] Home SOC Lab  [ ] Sleep"),
    ("",             ""),
    ("ToolBelt",     "Splunk | Elastic Stack | Wireshark | Kali Linux"),
    ("Core_Detect",  "SIEM | EDR | SOAR | Alert Triage"),
    ("Core_Offense", "Kali Linux | Mimikatz | PowerShell"),
    ("Core_Lang",    "Python | SQL | PowerShell | KQL / SPL"),
    ("Framework",    "MITRE ATT&CK | NIST CSF | Cyber Kill Chain"),
]

CONTACT = [
    ("mail",      "prajwalks.work@gmail.com"),
    ("linkedin",  "/in/prajwal-kuderu-suresh"),
    ("portfolio", "prajwal-kudedrusuresh.github.io/portfolio"),
    ("github",    "github.com/prajwal-kudedrusuresh"),
]

FOOTER = "See live GitHub stats below in README ^"

THEMES = {
    "dark": dict(
        bg="#0d1117", panel="#0d1117", border="#30363d",
        chrome_bg="#161b22", dot_colors=("#ff5f56", "#ffbd2e", "#27c93f"),
        title_color="#8b949e",
        ascii_color="#39d4ff",
        label_color="#7ee787", value_color="#c9d1d9",
        prompt_color="#58a6ff", footer_color="#8b949e",
        heading_color="#ff7b72",
    ),
    "light": dict(
        bg="#ffffff", panel="#ffffff", border="#d0d7de",
        chrome_bg="#f6f8fa", dot_colors=("#ff5f56", "#ffbd2e", "#27c93f"),
        title_color="#57606a",
        ascii_color="#0d1117",
        label_color="#0969da", value_color="#24292f",
        prompt_color="#8250df", footer_color="#57606a",
        heading_color="#cf222e",
    ),
}

def image_to_ascii(path, cols=70):
    img = Image.open(path).convert("L")
    w, h = img.size
    rows = max(1, round(cols * 0.5 * (h / w)))
    img = img.resize((cols, rows))
    pixels = list(img.getdata())
    grid_chars = []
    grid_alpha = []
    for r in range(rows):
        row_chars = []
        row_alpha = []
        for c in range(cols):
            b = pixels[r * cols + c]  # 0=black .. 255=white
            level = int((255 - b) / 255 * (len(RAMP) - 1))
            row_chars.append(RAMP[level])
            row_alpha.append(round((255 - b) / 255, 2))
        grid_chars.append(row_chars)
        grid_alpha.append(row_alpha)
    return grid_chars, grid_alpha, cols, rows


def rle_tspans(chars, alphas):
    """Collapse a row into tspans of (text, opacity) runs to keep SVG small."""
    runs = []
    cur_char_run = ""
    cur_alpha = None
    for ch, a in zip(chars, alphas):
        # bucket alpha into steps of 0.15 to merge similar runs
        bucket = round(a / 0.15) * 0.15
        if cur_alpha is None:
            cur_alpha = bucket
            cur_char_run = ch
        elif bucket == cur_alpha:
            cur_char_run += ch
        else:
            runs.append((cur_char_run, cur_alpha))
            cur_char_run = ch
            cur_alpha = bucket
    if cur_char_run:
        runs.append((cur_char_run, cur_alpha))
    return runs


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_svg(photo_path, theme_name):
    t = THEMES[theme_name]
    chars, alphas, cols, rows = image_to_ascii(photo_path, cols=66)

    W, H = 900, 460
    chrome_h = 34
    pad = 18

    ascii_font_size = 5.6
    char_w = ascii_font_size * 0.6
    line_h = ascii_font_size * 1.15
    ascii_x = pad
    ascii_y = chrome_h + pad + ascii_font_size

    ascii_lines_svg = []
    for r, (row_chars, row_alpha) in enumerate(zip(chars, alphas)):
        y = ascii_y + r * line_h
        tspans = []
        for text_run, alpha in rle_tspans(row_chars, row_alpha):
            tspans.append(
                f'<tspan fill="{t["ascii_color"]}" fill-opacity="{max(alpha,0.05)}">{esc(text_run)}</tspan>'
            )
        ascii_lines_svg.append(
            f'<text x="{ascii_x}" y="{y:.1f}" xml:space="preserve" font-family="Consolas, Menlo, monospace" font-size="{ascii_font_size}">{"".join(tspans)}</text>'
        )
    ascii_block_width = cols * char_w
    ascii_block_height = rows * line_h

    # ---- right info panel ----
    panel_x = ascii_x + ascii_block_width + 34
    panel_font = 13.5
    panel_line_h = 20
    y = chrome_h + pad + panel_font + 4

    info_svg = []
    info_svg.append(
        f'<text x="{panel_x}" y="{y:.1f}" font-family="Consolas, Menlo, monospace" font-size="14.5" font-weight="700" fill="{t["heading_color"]}">whoami --verbose</text>'
    )
    y += panel_line_h * 1.4

    label_w = 118
    for label, value in LINES:
        if not label:
            y += panel_line_h * 0.5
            continue
        info_svg.append(
            f'<text x="{panel_x}" y="{y:.1f}" font-family="Consolas, Menlo, monospace" font-size="{panel_font}" fill="{t["label_color"]}">{esc(label)}</text>'
        )
        info_svg.append(
            f'<text x="{panel_x + label_w}" y="{y:.1f}" font-family="Consolas, Menlo, monospace" font-size="{panel_font}" fill="{t["value_color"]}">{esc(value)}</text>'
        )
        y += panel_line_h

    y += panel_line_h * 0.3
    info_svg.append(
        f'<text x="{panel_x}" y="{y:.1f}" font-family="Consolas, Menlo, monospace" font-size="14.5" font-weight="700" fill="{t["heading_color"]}">contact --all</text>'
    )
    y += panel_line_h * 1.3
    for label, value in CONTACT:
        info_svg.append(
            f'<text x="{panel_x}" y="{y:.1f}" font-family="Consolas, Menlo, monospace" font-size="{panel_font}" fill="{t["prompt_color"]}">&gt;_ {esc(label)}</text>'
        )
        info_svg.append(
            f'<text x="{panel_x + 112}" y="{y:.1f}" font-family="Consolas, Menlo, monospace" font-size="{panel_font}" fill="{t["value_color"]}">{esc(value)}</text>'
        )
        y += panel_line_h

    y += panel_line_h * 0.6
    footer_y = y
    info_svg.append(
        f'<text x="{panel_x}" y="{footer_y:.1f}" font-family="Consolas, Menlo, monospace" font-size="12" fill="{t["footer_color"]}" font-style="italic">{esc(FOOTER)}</text>'
    )
    # blinking cursor
    info_svg.append(
        f'<rect x="{panel_x + len(FOOTER)*7.0:.1f}" y="{footer_y-11:.1f}" width="7" height="13" fill="{t["prompt_color"]}">'
        f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.4;0.5;0.9;1" dur="1.1s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    # scanline sweep over the ascii block
    scanline = (
        f'<rect x="{ascii_x}" y="{ascii_y - ascii_font_size}" width="{ascii_block_width:.1f}" height="2.2" '
        f'fill="{t["ascii_color"]}" opacity="0.35">'
        f'<animate attributeName="y" values="{ascii_y - ascii_font_size:.1f};{ascii_y - ascii_font_size + ascii_block_height:.1f}" '
        f'dur="3.2s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    dots = "".join(
        f'<circle cx="{18 + i*16}" cy="{chrome_h/2:.0f}" r="5" fill="{c}"/>'
        for i, c in enumerate(t["dot_colors"])
    )

    svg = f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{W}" height="{H}" rx="10" fill="{t['bg']}" stroke="{t['border']}"/>
  <path d="M0 10 a10 10 0 0 1 10 -10 h{W-20} a10 10 0 0 1 10 10 v{chrome_h-10} h-{W} z" fill="{t['chrome_bg']}"/>
  {dots}
  <text x="{W/2}" y="{chrome_h/2 + 4:.0f}" text-anchor="middle" font-family="Consolas, Menlo, monospace" font-size="12" fill="{t['title_color']}">prajwal-kudedrusuresh / README.md</text>
  <line x1="0" y1="{chrome_h}" x2="{W}" y2="{chrome_h}" stroke="{t['border']}"/>
  {"".join(ascii_lines_svg)}
  {scanline}
  <line x1="{panel_x - 20}" y1="{chrome_h+10}" x2="{panel_x - 20}" y2="{H-14}" stroke="{t['border']}"/>
  {"".join(info_svg)}
</svg>'''
    return svg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    for theme in ("dark", "light"):
        svg = build_svg(args.photo, theme)
        out_path = f"{args.out_dir}/{theme}.svg"
        with open(out_path, "w") as f:
            f.write(svg)
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
