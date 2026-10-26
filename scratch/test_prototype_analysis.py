import io
from PIL import Image, ImageDraw

def test_prototype_image_analysis():
    # 1. Simulate Lamport Logical Clock image
    img = Image.new('RGB', (800, 450), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Title
    draw.text((250, 20), "Lamport's Logical Clock Synchronization", fill=(0, 0, 0))
    # Three horizontal process lines
    for y, label in [(100, "P1"), (200, "P2"), (300, "P3")]:
        draw.text((50, y - 10), label, fill=(0, 0, 150))
        draw.line([(90, y), (750, y)], fill=(0, 0, 0), width=3)
        # Events
        for x in [150, 300, 450, 600]:
            draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(200, 0, 0))
    # Message arrows
    draw.line([(150, 100), (300, 200)], fill=(0, 150, 0), width=2)
    draw.line([(300, 200), (450, 300)], fill=(0, 150, 0), width=2)

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    content = img_bytes.getvalue()

    original_filename = "lamports algorithm.jpg"
    print("Testing original_filename:", repr(original_filename))
    assert " " in original_filename, "Filename must retain spaces"
    assert original_filename.endswith(".jpg")

    width, height = img.size
    aspect_ratio = round(width / max(1, height), 2)
    print(f"Dimensions: {width}x{height}, Aspect ratio: {aspect_ratio}")
    assert aspect_ratio > 1.3, "Timeline diagrams have wide aspect ratio"

    print("Prototype image created and verified successfully!")

test_prototype_image_analysis()
