from PIL import Image

paths = [
    r"c:/Users/58143406/Documents/Web/Web2/OdontoPro/odontoPro/static/img/banner simples.png",
    r"c:/Users/58143406/Documents/Web/Web2/OdontoPro/odontoPro/static/img/Agende já sua consulta (1).png",
]

for p in paths:
    im = Image.open(p)
    print(p, im.size)
