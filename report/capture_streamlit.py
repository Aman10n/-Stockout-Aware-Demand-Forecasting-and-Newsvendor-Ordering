"""Capture screenshots of every tab of the Streamlit planner (planner/app.py) running on :8501."""
import sys, time
from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent / "assets" / "streamlit"
OUT.mkdir(parents=True, exist_ok=True)
URL = "http://localhost:8501/"
TABS = ["Order planner (live model)", "Network KPIs", "Research results (9 policies)",
        "Power BI report", "Batch scoring", "About the data"]

def trim(path):
    im = Image.open(path).convert("RGB")
    bg = Image.new("RGB", im.size, im.getpixel((im.width - 2, im.height - 2)))
    box = ImageChops.difference(im, bg).getbbox()
    if box:
        im = im.crop((0, 0, im.width, min(im.height, box[3] + 30)))
    im.save(path)

def wait_idle(page, extra=2.5):
    # Streamlit shows a "running" status widget while scripts execute
    for _ in range(120):
        if page.locator('[data-testid="stStatusWidget"]').count() == 0:
            break
        time.sleep(0.5)
    time.sleep(extra)

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    pg = b.new_page(viewport={"width": 1600, "height": 2600}, device_scale_factor=1.5)
    pg.goto(URL, wait_until="networkidle")
    pg.wait_for_selector('[data-baseweb="tab"]', timeout=180000)
    wait_idle(pg, 6)
    for i, name in enumerate(TABS, 1):
        pg.get_by_role("tab", name=name).click()
        wait_idle(pg, 4)
        f = OUT / f"st{i}_{name.split(' (')[0].lower().replace(' ', '_')}.png"
        pg.screenshot(path=str(f))
        trim(f)
        print("saved", f.name)
    # also a viewport-sized hero shot of the first tab
    pg.set_viewport_size({"width": 1600, "height": 950})
    pg.get_by_role("tab", name=TABS[0]).click()
    wait_idle(pg, 3)
    pg.screenshot(path=str(OUT / "st0_hero.png"))
    b.close()
