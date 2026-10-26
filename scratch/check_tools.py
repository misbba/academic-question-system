import shutil

print("tesseract on PATH:", shutil.which("tesseract"))
for common in [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\Nisha\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
]:
    import os
    if os.path.exists(common):
        print("Found tesseract at:", common)

try:
    import PIL
    print("PIL version:", PIL.__version__)
except Exception as e:
    print("PIL error:", e)

try:
    import pytesseract
    print("pytesseract installed")
except Exception as e:
    print("pytesseract error:", e)

try:
    import cv2
    print("cv2 installed")
except Exception as e:
    print("cv2 error:", e)
