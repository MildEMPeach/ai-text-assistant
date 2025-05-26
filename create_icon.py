from PIL import Image, ImageDraw

# Create a new image with a transparent background
size = (64, 64)
image = Image.new('RGBA', size, (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Draw a simple "T" shape
draw.rectangle([16, 12, 48, 20], fill=(65, 105, 225))  # Top horizontal line
draw.rectangle([28, 12, 36, 52], fill=(65, 105, 225))  # Vertical line

# Save the icon
image.save('icon.png') 