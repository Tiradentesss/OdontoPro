from PIL import Image, ImageOps
import os

base = r"c:/Users/58143406/Documents/Web/Web2/OdontoPro/odontoPro/static/img"

banners = [
    ("banner simples.png", "banner1"),
    ("Agende já sua consulta (1).png", "banner2"),
]

sizes = {
    "mobile": (480, 192),
    "desktop": (1200, 480),
}

for filename, prefix in banners:
    path = os.path.join(base, filename)
    im = Image.open(path)
    for label, size in sizes.items():
        out = ImageOps.fit(im, size, Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        out_path = os.path.join(base, f"{prefix}-{label}.png")
        out.save(out_path, optimize=True, quality=85)
        print(f"Saved {out_path} ({size})")
