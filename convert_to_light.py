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

    # Calculate lightness / perceived brightness
    # Standard luminance weights
    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]

    # Convert dark theme to clean light theme:
    # Invert background darkness while keeping colorful accents vibrant
    
    # Background mask: where luminance is low (dark areas)
    # Smooth transition from dark (0.0) to bright (1.0)
    bg_mask = np.clip((0.45 - lum) / 0.45, 0.0, 1.0)
    
    # Invert base channels
    inv_arr = 1.0 - arr
    
    # We want a stylish, clean crisp light background (tinted very slightly cool/slate #F8FAFC)
    # Brighten and soften inverted dark tones
    light_bg = 0.96 * inv_arr + 0.04
    
    # For bright elements (white text, bright neon glows):
    # White text (high luminance, low saturation) should turn into deep navy/charcoal for crisp contrast
    # Calculate saturation
    max_c = np.maximum(np.maximum(arr[:, :, 0], arr[:, :, 1]), arr[:, :, 2])
    min_c = np.minimum(np.minimum(arr[:, :, 0], arr[:, :, 1]), arr[:, :, 2])
    sat = np.where(max_c > 0, (max_c - min_c) / (max_c + 1e-6), 0.0)
    
    # White text mask: high lum, low sat
    white_text_mask = np.clip((lum - 0.6) / 0.3, 0.0, 1.0) * np.clip((0.3 - sat) / 0.3, 0.0, 1.0)
    
    # Neon colored elements: high saturation, medium/high lum -> enhance saturation & contrast
    colored_mask = np.clip((sat - 0.2) / 0.5, 0.0, 1.0)
    
    # Base composite
    res = arr.copy()
    
    # 1. Turn dark backgrounds into clean light-grey/white
    for c in range(3):
        # Invert tone with gamma curve
        res[:, :, c] = np.where(bg_mask > 0, 
                                (1.0 - (arr[:, :, c] ** 0.65)) * 0.96 + 0.04, 
                                arr[:, :, c])
    
    # 2. Make white text dark charcoal (#0F172A)
    charcoal = np.array([0.06, 0.09, 0.16], dtype=np.float32)
    for c in range(3):
        res[:, :, c] = res[:, :, c] * (1.0 - white_text_mask) + charcoal[c] * white_text_mask

    # 3. Enhance colorful accents and neons so they pop on white
    res = np.clip(res, 0.0, 1.0)
    res_uint8 = (res * 255).astype(np.uint8)
    res_img = Image.fromarray(res_uint8)
    
    # Boost color vibrancy slightly
    enhancer = ImageEnhance.Color(res_img)
    res_img = enhancer.enhance(1.25)
    
    enhancer_con = ImageEnhance.Contrast(res_img)
    res_img = enhancer_con.enhance(1.15)
    
    # Save as WebP / PNG
    res_img.save(out_path, quality=95)
    print(f"Processed: {os.path.basename(img_path)} -> {os.path.basename(out_path)}")

# Process all files
for f in sorted(glob.glob(os.path.join(src_dir, "*"))):
    name = os.path.basename(f)
    out_file = os.path.join(dst_dir, name)
    process_image(f, out_file)

print("Done! All images in light theme generated in:", dst_dir)
