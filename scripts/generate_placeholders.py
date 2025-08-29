from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(text, filename, size=(200, 200), bg_color=(228, 30, 49), text_color=(255, 255, 255)):
    # Create new image with a background color
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Calculate text position (center)
    text_bbox = draw.textbbox((0, 0), text)
    text_x = (size[0] - (text_bbox[2] - text_bbox[0])) / 2
    text_y = (size[1] - (text_bbox[3] - text_bbox[1])) / 2
    
    # Draw text
    draw.text((text_x, text_y), text, fill=text_color)
    
    # Save image
    img.save(filename)

def main():
    # Create directories if they don't exist
    os.makedirs('public/images', exist_ok=True)
    os.makedirs('public/images/news', exist_ok=True)
    
    # Create placeholder images
    images = {
        'public/images/fallback.jpg': 'News',
        'public/images/news/technology.jpg': 'Technology',
        'public/images/news/business.jpg': 'Business',
        'public/images/news/science.jpg': 'Science',
        'public/images/news/climate-summit.jpg': 'Climate',
        'public/images/icon-192.png': 'NSA'
    }
    
    for filename, text in images.items():
        create_placeholder_image(text, filename)

if __name__ == '__main__':
    main()
