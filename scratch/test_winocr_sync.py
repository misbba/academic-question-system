import winocr
from PIL import Image, ImageDraw

img = Image.new('RGB', (600, 200), color=(255, 255, 255))
draw = ImageDraw.Draw(img)
draw.text((20, 30), "Lamport's Logical Clock Diagram", fill=(0, 0, 0))
draw.text((20, 70), "Process P1 -> Event e1 -> Message m1", fill=(0, 0, 0))

try:
    res = winocr.recognize_pil_sync(img, lang="en")
    print("winocr.recognize_pil_sync result type:", type(res))
    print("result content:", res)
    if isinstance(res, dict):
        print("text:", res.get('text'))
        for line in res.get('lines', []):
            print("Line:", line.get('text'))
except Exception as e:
    print("Error:", e)
