import os
import glob
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

src_dir = "/home/grapeonwheels/Websites/doksintez/static/img/good"
dst_dir = "/home/grapeonwheels/Websites/doksintez/static/img/good_light"
os.makedirs(dst_dir, exist_ok=True)

def process_image(img_path, out_path):
    img = Image.open(img_path).convert("RGB")
    arr = np.array(img, dtype=np.float32) / 255.0

    # Luminance
    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    
    # Saturation
    max_c = np.maximum(np.maximum(arr[:, :, 0], arr[:, :, 1]), arr[:, :, 2])
    min_c = np.minimum(np.minimum(arr[:, :, 0], arr[:, :, 1]), arr[:, :, 2])
    sat = np.where(max_c > 0, (max_c - min_c) / (max_c + 1e-6), 0.0)

    # Clean Pure Light Theme mapping:
    # 1. Dark backgrounds (lum < 0.25) -> Crisp Clean White / Off-white (#F8FAFC - #FFFFFF)
    # 2. Text / Headers (lum > 0.6, sat < 0.35) -> Deep Navy / Charcoal (#0F172A)
    # 3. Colors & Neons -> Keep their vivid hue, adjust luminance so they contrast on light background
    
    # Inverted luminance for background
    bg_factor = np.clip((0.35 - lum) / 0.35, 0.0, 1.0)
    
    # Initialize output array
    out = arr.copy()
    
    # Background replacement: smooth gradient towards #F8FAFC
    # Calculate neutral slate light bg
    slate_white = np.array([0.965, 0.975, 0.985], dtype=np.float32)
    
    for c in range(3):
        # Blend dark areas into clean white/slate
        out[:, :, c] = out[:, :, c] * (1.0 - bg_factor) + slate_white[c] * bg_factor

    # Darken pure white text to deep dark slate #0F172A for high readability
    white_text_mask = np.clip((lum - 0.55) / 0.25, 0.0, 1.0) * np.clip((0.35 - sat) / 0.35, 0.0, 1.0)
    # Exclude bright colored elements
    white_text_mask = white_text_mask * (1.0 - bg_factor)
    
    text_color = np.array([0.06, 0.09, 0.16], dtype=np.float32)
    for c in range(3):
        out[:, :, c] = out[:, :, c] * (1.0 - white_text_mask) + text_color[c] * white_text_mask

    # Preserve and enhance colored lines/boxes
    out = np.clip(out, 0.0, 1.0)
    res_uint8 = (out * 255).astype(np.uint8)
    res_img = Image.fromarray(res_uint8)
    
    # Contrast & Color optimization
    res_img = ImageEnhance.Color(res_img).enhance(1.15)
    res_img = ImageEnhance.Contrast(res_img).enhance(1.10)
    
    res_img.save(out_path, quality=95)
    print(f"Enhanced Light: {os.path.basename(img_path)} -> {os.path.basename(out_path)}")

for f in sorted(glob.glob(os.path.join(src_dir, "*"))):
    name = os.path.basename(f)
    out_file = os.path.join(dst_dir, name)
    process_image(f, out_file)

print("Professional light theme set generated!")
