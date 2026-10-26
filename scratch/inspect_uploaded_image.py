from PIL import Image
import os

img_path = r"backend/uploads/resources/diagram_1792998088_lamports_algorithm.jpg"
if os.path.exists(img_path):
    im = Image.open(img_path)
    print("Size:", im.size)
    print("Format:", im.format)
    print("Mode:", im.mode)
else:
    print("File not found")
