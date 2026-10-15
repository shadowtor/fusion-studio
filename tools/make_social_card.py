#!/usr/bin/env python3
"""Render the 1280x640 social card (GitHub repo social preview, link previews) to site/social-card.png.

  python tools/make_social_card.py

Uses the transparent screenshot of the example model, a headless Chromium-based browser and Schibsted Grotesk (SIL OFL)
from Google Fonts. All content sits inside an 80 px safe area. Matches the look of the brand-studio card (same grid, type, blue).
"""
import base64, io, os, re, shutil, subprocess, sys, tempfile, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, SAFE = 1280, 640, 80
OUT = os.path.join(ROOT, "site", "social-card.png")
SHOT = os.path.join(ROOT, "examples", "monster-can-holder", "iso-transparent.png")


def font_face(weight):
    css = urllib.request.urlopen(urllib.request.Request(
        f"https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@{weight}",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 Chrome/120 Safari/537.36"}), timeout=30).read().decode()
    url = re.search(r"url\((https://[^)]+)\)", css).group(1)
    b64 = base64.b64encode(urllib.request.urlopen(url, timeout=30).read()).decode("ascii")
    return f"@font-face{{font-family:'SG';font-weight:{weight};src:url(data:font/ttf;base64,{b64})}}"


def model_uri():
    from PIL import Image
    im = Image.open(SHOT).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def browser():
    for p in (shutil.which("chrome"), shutil.which("msedge"), shutil.which("chromium"), shutil.which("google-chrome"),
              r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"):
        if p and os.path.exists(p):
            return p
    sys.exit("No Chromium-based browser found")


chips = "".join(f'<span class="chip{" on" if i == 0 else ""}">{t}</span>' for i, t in enumerate(["Print", "Showcase", "Apparel"]))
html = f"""<!doctype html><meta charset="utf-8"><style>
{font_face(400)}{font_face(600)}{font_face(800)}
*{{box-sizing:border-box}}html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden}}
body{{background:#eef1f4;color:#14181f;font:400 24px/1.4 'SG',sans-serif;position:relative;
background-image:linear-gradient(rgba(20,24,31,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(20,24,31,.06) 1px,transparent 1px);background-size:32px 32px}}
.safe{{position:absolute;left:{SAFE}px;top:{SAFE}px;right:{SAFE}px;bottom:{SAFE}px;display:grid;grid-template-columns:540px 1fr;gap:48px;align-items:center}}
.name{{font-weight:800;font-size:30px;letter-spacing:-.01em;margin-bottom:22px}}
h1{{margin:0;font-weight:800;font-size:54px;line-height:1.05;letter-spacing:-.02em}}
p{{margin:22px 0 0;color:#4f5966;font-size:24px;line-height:1.35}}
.chips{{display:flex;gap:10px;margin-top:26px}}
.chip{{border:2px solid #14181f;padding:4px 14px;font-weight:600;font-size:20px;background:#fff}}
.chip.on{{background:#1f5fd6;border-color:#1f5fd6;color:#fff}}
.tile{{height:400px;background:#fff;position:relative;display:grid;place-items:center;box-shadow:0 1px 0 rgba(20,24,31,.2)}}
.tile img{{height:300px;max-width:88%;object-fit:contain;margin-bottom:34px}}
.tile::before{{content:"";position:absolute;top:10px;left:10px;width:14px;height:14px;border-top:1px solid #14181f;border-left:1px solid #14181f;opacity:.5}}
.dim{{position:absolute;left:10%;right:10%;bottom:26px;border-top:1px solid #1f5fd6;text-align:center;color:#1f5fd6;font-size:17px;font-weight:600;padding-top:3px}}
.tag{{position:absolute;right:12px;top:8px;font-size:15px;color:#4f5966}}
</style><body><div class="safe"><div>
<div class="name">fusion-studio</div>
<h1>Design in Fusion with your AI agent. Built to print.</h1>
<p>Parametric models from your measurements. An Agent Skill, tested with Claude Code.</p>
<div class="chips">{chips}</div></div>
<div class="tile"><img src="{model_uri()}"><span class="tag">PETG</span><div class="dim">can_dia = 66 mm</div></div></div></body>"""

with tempfile.TemporaryDirectory() as td:
    f = os.path.join(td, "card.html")
    open(f, "w", encoding="utf-8").write(html)
    subprocess.check_call([browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}",
                           f"--screenshot={OUT}", "file:///" + f.replace(os.sep, "/")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"wrote {OUT}  {os.path.getsize(OUT) / 1024:.0f} KB")
