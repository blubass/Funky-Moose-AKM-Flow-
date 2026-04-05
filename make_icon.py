
from PIL import Image

input_image = "icon.png"
output_icon = "icon.icns"

sizes = [16, 32, 64, 128, 256, 512, 1024]

img = Image.open(input_image)

img.save(output_icon, sizes=[(s, s) for s in sizes])

print("icon.icns erstellt")
