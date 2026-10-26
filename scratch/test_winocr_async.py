import asyncio
import winocr
from PIL import Image, ImageDraw

img = Image.new('RGB', (600, 200), color=(255, 255, 255))
draw = ImageDraw.Draw(img)
draw.text((20, 30), "Lamport's Logical Clock Diagram", fill=(0, 0, 0))
draw.text((20, 70), "Process P1 -> Event e1 -> Message m1", fill=(0, 0, 0))

async def main():
    res = await winocr.recognize_pil(img, lang="en")
    print("Async winocr res:", res)
    if hasattr(res, 'text'):
        print("res.text:", res.text)
    elif isinstance(res, dict):
        print("res dict:", res)
    else:
        print("dir(res):", dir(res))

asyncio.run(main())
