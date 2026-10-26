import winocr
from PIL import Image, ImageDraw

# Create image with text
img = Image.new('RGB', (500, 150), color=(255, 255, 255))
draw = ImageDraw.Draw(img)
draw.text((20, 30), "Lamport's Logical Clock Diagram", fill=(0, 0, 0))
draw.text((20, 70), "Process P1 -> Event e1 -> Message m1", fill=(0, 0, 0))

test_path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\scratch\test_ocr_sample.png"
img.save(test_path)

try:
    result = winocr.recognize_pil(img, lang="en")
    print("winocr.recognize_pil result:", result)
    text = result.get('text', '') if isinstance(result, dict) else str(result)
    print("Extracted text:", text)
except Exception as e:
    print("winocr error:", e)
