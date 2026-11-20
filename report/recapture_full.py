import time
from pathlib import Path
from playwright.sync_api import sync_playwright
OUT = Path(__file__).resolve().parent / "assets" / "simulator"
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]
CSS = ".topbar{position:static !important}"
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True, args=ARGS)
    pg = b.new_page(viewport={"width": 1500, "height": 900}, device_scale_factor=1.5)
    pg.goto("http://localhost:3000/#command", wait_until="networkidle"); pg.add_style_tag(content=CSS); time.sleep(8)
    pg.screenshot(path=str(OUT/"sim1_command_full.png"), full_page=True)
    pg.goto("http://localhost:3000/#lab", wait_until="networkidle"); pg.add_style_tag(content=CSS); time.sleep(7)
    btn = pg.locator("button", has_text="Run mechanism"); btn.first.click()
    for _ in range(120):
        if "Running" not in btn.first.inner_text(): break
        time.sleep(1)
    time.sleep(3); pg.screenshot(path=str(OUT/"sim3_lab_batch.png"), full_page=True)
    pg.get_by_text("C · no refill").first.click(); time.sleep(5)
    pg.screenshot(path=str(OUT/"sim3_lab_mechC.png"), full_page=False)
    pg.goto("http://localhost:3000/#xray", wait_until="networkidle"); pg.add_style_tag(content=CSS); time.sleep(8)
    pg.screenshot(path=str(OUT/"sim4_xray_full.png"), full_page=True)
    b.close()
print("done")
