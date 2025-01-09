from PIL import Image

# Convert an image to a string of hexadecimal values
def image_to_rgb_string(image_path):
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
        
        pixel_string = ""
        
        width, height = img.size
        
        for y in range(height):
            for x in range(width):
                r, g, b = img.getpixel((x, y))
                pixel_string += f"{r:02x}{g:02x}{b:02x}"
        
        return pixel_string
    except Exception as e:
        print(f"[ERROR] : {e}")
        return None

# Create an hex frame from a 9x16 character img
# For 16 lines, convert the first 9 pixels to a 2 bytes hex value
# bit shift the 9 bits to the left by 7.
# if the pixel is white, add 1 bit, else add 0
def charimg_to_hex_string(image_path):
    # Load the image
    img = Image.open(image_path).convert("L")

    # Check if the image is 9x16 pixels
    if img.size != (9, 16):
        raise ValueError("L'image doit être de taille 9x16 pixels.")

    hex_string = ""

    for y in range(16):
        line_value = 0

        for x in range(9):
            pixel = img.getpixel((x, y))
            if pixel > 0:
                line_value |= (1 << (15 - x))  # Move the bit to the left by 7

        # Convert the value to a 4 bytes hex string
        hex_string += f"{line_value:04X}"

    return hex_string