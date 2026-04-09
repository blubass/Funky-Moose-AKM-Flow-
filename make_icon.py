from PIL import Image
from pathlib import Path


input_image = "icon.png"
output_icns = "akm_icon.icns"
output_ico = "akm_icon.ico"

img = Image.open(input_image)
created = []
if not Path(output_icns).exists():
    img.save(output_icns, sizes=[(s, s) for s in (16, 32, 64, 128, 256, 512, 1024)])
    created.append(output_icns)
img.save(output_ico, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
created.append(output_ico)

print(", ".join(created) + " erstellt")
