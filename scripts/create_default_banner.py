from PIL import Image
import os

src = os.path.join('odontoPro', 'static', 'img', 'banner simples.png')
dst = os.path.join('odontoPro', 'static', 'img', 'default-banner.jpg')

print('src', src)
print('dst', dst)

img = Image.open(src)
img = img.convert('RGB')
img.save(dst, format='JPEG', quality=90)
print('created', dst)
