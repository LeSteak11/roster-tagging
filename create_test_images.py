"""
Test script to create sample images for testing the UI
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image(filename, username, width=400, height=300):
    """Create a test image with text overlay"""
    # Create a colored background
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    color = colors[hash(username) % len(colors)]
    
    image = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(image)
    
    # Add text
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        font = None
    
    text = f"Test Image\n{username}"
    
    # Get text bounding box
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width, text_height = 100, 50
    
    # Center the text
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill='white', font=font)
    
    return image

def create_test_images():
    """Create test images following the naming convention"""
    test_dir = "test_images"
    
    # Test data with usernames and multiple images per user
    test_data = [
        ("alana_moore", 5),
        ("jessica_smith", 3),
        ("maria_garcia", 7),
        ("sophie_wilson", 2),
        ("emma_johnson", 4)
    ]
    
    print(f"Creating test images in {test_dir}/")
    
    for username, count in test_data:
        for i in range(count):
            # Generate filename with random numbers
            numbers = f"{1000000 + i * 123456 + hash(username) % 1000000}"
            filename = f"{username}_{numbers}.jpg"
            filepath = os.path.join(test_dir, filename)
            
            # Create and save image
            image = create_test_image(filename, username)
            image.save(filepath, "JPEG")
            print(f"  Created: {filename}")
    
    print(f"\n✅ Test images created successfully!")
    print(f"📁 Test folder: {os.path.abspath(test_dir)}")
    print(f"📌 Use this path in the Streamlit app to test the functionality")

if __name__ == "__main__":
    create_test_images()