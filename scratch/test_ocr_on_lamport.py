from PIL import Image
import os

img_path = r"backend/uploads/resources/diagram_1792998088_lamports_algorithm.jpg"
im = Image.open(img_path)

print("Testing pytesseract...")
try:
    import pytesseract
    text = pytesseract.image_to_string(im)
    print("Tesseract text:", repr(text[:300]))
except Exception as e:
    print("Tesseract failed:", e)

print("\nTesting winocr...")
try:
    import winocr
    import asyncio
    res = asyncio.run(winocr.recognize_pil(im, 'en'))
    print("WinOCR text:", repr(res.text[:300]))
except Exception as e:
    print("WinOCR failed:", e)
