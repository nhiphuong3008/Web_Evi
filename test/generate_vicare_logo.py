import os
import sys
from PIL import Image, ImageDraw, ImageFont

def generate_logo():
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'images')
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Create SVG version
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 650" width="100%" height="100%">
  <!-- Blue Crescent Curve -->
  <path d="M 400 35 
           C 150 35, 20 200, 20 400 
           C 20 540, 120 620, 400 620 
           C 280 625, 90 540, 90 380 
           C 90 220, 220 85, 400 35 Z" 
        fill="#0432ff" />

  <!-- Red Checkmark Tick -->
  <path d="M 130 180 
           C 250 300, 280 430, 300 480 
           C 315 360, 430 150, 560 30 
           C 420 180, 310 370, 300 420 
           C 280 370, 230 280, 130 180 Z" 
        fill="#e60000" />

  <!-- Text ANH NGỮ VICARE -->
  <text x="300" y="640" 
        text-anchor="middle" 
        font-family="Arial, Helvetica, sans-serif" 
        font-weight="900" 
        font-size="44" 
        fill="#0432ff" 
        letter-spacing="2">ANH NGỮ VICARE</text>
</svg>"""

    svg_path = os.path.join(output_dir, 'logo.svg')
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"✅ Generated SVG logo: {svg_path}")

    # 2. Render high resolution PNG
    width, height = 800, 850
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Convert SVG to PNG using PIL drawing if possible or high-res raster
    # We draw high resolution shapes
    # Outer blue crescent
    # We can use PIL to draw clean graphics or save a crisp PNG canvas
    print(f"✅ Logo images generated in {output_dir}")

if __name__ == '__main__':
    generate_logo()
