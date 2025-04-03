from PIL import Image, ImageDraw, ImageFont
import os

# Create the media directory if it doesn't exist
os.makedirs('media', exist_ok=True)

# Create a 300x300 gray image
img = Image.new('RGB', (300, 300), color=(200, 200, 200))
draw = ImageDraw.Draw(img)

# Draw a silhouette-like figure
# Draw head
draw.ellipse((100, 50, 200, 150), fill=(150, 150, 150))
# Draw body
draw.ellipse((75, 150, 225, 350), fill=(150, 150, 150))

# Add text
try:
    # Try to use a system font
    font = ImageFont.truetype("Arial", 24)
except IOError:
    # Fall back to default
    font = ImageFont.load_default()

draw.text((150, 200), "Profile", fill=(100, 100, 100), anchor="mm", font=font)

# Save the image
img.save('media/default.jpg')

print("Default profile image created successfully!")