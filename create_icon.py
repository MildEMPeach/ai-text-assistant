from PIL import Image, ImageDraw, ImageFont

# Create a new image with a transparent background
size = (64, 64)
image = Image.new('RGBA', size, (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Define colors for the M
primary_color = (255, 215, 0)        # Golden yellow
shadow_color = (218, 165, 32)        # Darker golden yellow for depth
background_color = (255, 255, 224)   # Light yellow background (optional)

# Option 1: Simple geometric M
# Create a rounded rectangle background (optional)
# draw.rounded_rectangle([4, 4, 60, 60], radius=8, fill=background_color)

# Draw the letter M using lines/rectangles
# Left vertical line
draw.rectangle([12, 16, 18, 48], fill=primary_color)

# Right vertical line  
draw.rectangle([46, 16, 52, 48], fill=primary_color)

# Left diagonal line (top-left to center)
# Using a series of small rectangles to create diagonal
for i in range(16):
    x = 18 + i * 1.0
    y = 16 + i * 1.0
    draw.rectangle([x, y, x+3, y+3], fill=primary_color)

# Right diagonal line (top-right to center)
for i in range(16):
    x = 46 - i * 1.0
    y = 16 + i * 1.0
    draw.rectangle([x, y, x+3, y+3], fill=primary_color)

# Add subtle shadow/depth effect
# Left vertical shadow
draw.rectangle([13, 17, 19, 49], fill=shadow_color)

# Right vertical shadow
draw.rectangle([47, 17, 53, 49], fill=shadow_color)

# Save the icon
image.save('icon.png') 