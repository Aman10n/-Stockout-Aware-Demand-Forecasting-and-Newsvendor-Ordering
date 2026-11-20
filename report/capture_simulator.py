"""Capture clean screenshots of the 3D simulator (simulator/, served on :3000)."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent / "assets" / "simulator"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "http://localhost:3000/"
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--enable-webgl"]

def shot(pg, name, full=True, wait=4):
    time.sleep(wait)
    pg.screenshot(path=str(OUT / name), full_page=full)
    print("saved", name)

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True, args=ARGS)
    pg = b.new_page(viewport={"width": 1500, "height": 900}, device_scale_factor=1.5)
    pg.on("console", lambda m: m.type == "error" and print("console:", m.text[:150]))

    pg.goto(BASE + "#command", wait_until="networkidle"); shot(pg, "sim1_command_top.png", full=False, wait=8)
    shot(pg, "sim1_command_full.png", full=True, wait=1)
    pg.get_by_text("Shortage more costly", exact=True).first.click(); shot(pg, "sim1_command_shortage.png", full=False, wait=4)

    pg.goto(BASE + "?store=891#game", wait_until="networkidle"); shot(pg, "sim2_game_setup.png", full=False, wait=6)
    pg.get_by_role("button", name="▶ Start the week").click(); shot(pg, "sim2_game_morning.png", full=True, wait=6)
    pg.get_by_role("button", name="Use AI orders").click(); time.sleep(1)
    pg.get_by_role("button", name="▶ Open the store").click(); shot(pg, "sim2_game_open.png", full=False, wait=7)
    # wait for the day to close
    for _ in range(90):
        if pg.get_by_role("button", name="Next day ▶").count() or pg.get_by_role("button", name="See the week results").count():
            break
        time.sleep(1)
    shot(pg, "sim2_game_close.png", full=True, wait=2)
    # play out the week with AI orders
    for day in range(7):
        nb = pg.get_by_role("button", name="See the week results")
        if nb.count():
            nb.click(); break
        pg.get_by_role("button", name="Next day ▶").click(); time.sleep(3)
        if pg.get_by_role("button", name="Use AI orders").count():
            pg.get_by_role("button", name="Use AI orders").click(); time.sleep(0.5)
            pg.get_by_role("button", name="▶ Open the store").click()
        for _ in range(90):
            if pg.get_by_role("button", name="Next day ▶").count() or pg.get_by_role("button", name="See the week results").count():
                break
            time.sleep(1)
    shot(pg, "sim2_game_final.png", full=True, wait=5)

    pg.goto(BASE + "#lab", wait_until="networkidle"); shot(pg, "sim3_lab_top.png", full=False, wait=7)
    shot(pg, "sim3_lab_full.png", full=True, wait=1)
    btn = pg.locator("button", has_text="Run mechanism")
    if btn.count():
        btn.first.click()
        for _ in range(120):
            if "Running" not in btn.first.inner_text(): break
            time.sleep(1)
        shot(pg, "sim3_lab_batch.png", full=True, wait=3)

    pg.goto(BASE + "#xray", wait_until="networkidle"); shot(pg, "sim4_xray_top.png", full=False, wait=8)
    shot(pg, "sim4_xray_full.png", full=True, wait=1)
    b.close()
