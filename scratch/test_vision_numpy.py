import os
import numpy as np
from PIL import Image

img_path = r"backend/uploads/resources/diagram_1792998088_lamports_algorithm.jpg"
im = Image.open(img_path)
w, h = im.size
print(f"Image Size: {w}x{h}, Mode: {im.mode}")

# Convert to grayscale array
gray = np.array(im.convert('L'), dtype=np.float32)
# Background analysis
mean_brightness = float(np.mean(gray))
std_brightness = float(np.std(gray))
print(f"Mean Brightness: {mean_brightness:.1f}, Std: {std_brightness:.1f}")

# Threshold for lines/strokes (assuming light background if mean > 128)
is_light_bg = mean_brightness > 128
strokes = (gray < 100) if is_light_bg else (gray > 150)
stroke_ratio = float(np.mean(strokes))
print(f"Stroke pixel ratio: {stroke_ratio:.3f}")

# Horizontal line energy (sum across rows)
row_sums = np.sum(strokes, axis=1)
# Peaks in row_sums indicate prominent horizontal lifelines/boundaries
high_density_rows = np.where(row_sums > (w * 0.25))[0]
print(f"Prominent horizontal line row count: {len(high_density_rows)}")

print("Analysis successfully executed!")
