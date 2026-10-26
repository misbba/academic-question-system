import io
import os
import time
from PIL import Image

# Create a test PNG image in memory
img_byte_arr = io.BytesIO()
test_img = Image.new('RGB', (300, 200), color='blue')
test_img.save(img_byte_arr, format='PNG')
img_bytes = img_byte_arr.getvalue()

print(f"Generated test PNG bytes: {len(img_bytes)} bytes")

# Verify PIL can open and verify it
opened = Image.open(io.BytesIO(img_bytes))
print(f"Image format: {opened.format}, size: {opened.size}")
opened.verify()
print("Image verification passed!")
