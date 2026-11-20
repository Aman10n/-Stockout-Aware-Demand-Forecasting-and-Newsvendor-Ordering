from pathlib import Path
from PIL import Image, ImageChops
d = Path("assets/streamlit")
for f in sorted(d.glob("st[1-6]_*.png")):
    im = Image.open(f).convert("RGB")
    main = im.crop((480, 0, im.width, im.height))
    bg = Image.new("RGB", main.size, (255, 255, 255))
    box = ImageChops.difference(main, bg).getbbox()
    if box:
        im = im.crop((0, 0, im.width, min(im.height, box[3] + 40)))
        im.save(f)
    print(f.name, im.size)
