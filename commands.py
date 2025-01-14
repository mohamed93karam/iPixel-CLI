from bit_tools import *
from img_2_pix import image_to_rgb_string
from img_2_pix import charimg_to_hex_string

# Set the clock mode
def set_clock_mode(value: int = 1):
    # Sending {11, 0, 6, 1}, then clock to display (then Years, Month, Days, "weekOfDate" ?)
    
    try:
        value = int(value)
    except ValueError as e:
        raise ValueError(f"Invalid parameter type: {e}")
    
    # Check if the value is within the valid range
    if not 0 <= value <= 8:
        raise ValueError("Clock mode must be between 1 and 8 or 0 for disabled")
    
    header = bytes.fromhex("0b000601")
    parameter = bytes.fromhex(int2hex(value))
    end = bytes.fromhex("0100e80c0706")

    return header + parameter + end

# Set the DIY Fun Mode (Drawing Mode)
# Screen will not be saved in the EEPROM
def set_fun_mode(value: bool):
    # Send {5, 0, 4, 1, 1}
    data = bytes.fromhex("05000401")
    if value:
        data += bytes.fromhex("01")
    else:
        data += bytes.fromhex("00")
    return data
    
# Set the screen orientation
def set_orientation():
    # Send {5, 0, 6, ByteCompanionObject.MIN_VALUE ???, 0}
    #data = bytes.fromhex("0500060000")
    return

# Wipe the EEPROM (Reset)
def clear():
    return bytes.fromhex("04000380")

# Set the device brightness
# Value must be between 0 and 100
def set_brightness(value: int):
    # Send 5, 0, 4, + byte companion code (0x80 = 128) + Brightness (0 to 100)
    header = bytes.fromhex("05000480")
    parameter = bytes.fromhex(str(value).zfill(2))

    return header + parameter

# Set the speed of the animation
def set_speed(value:int):
    header = bytes.fromhex("050003")
    parameter = bytes.fromhex(int2hex(value)) # Sur 4 hexa (2 octets)
    
    return header + parameter

# UNTESTED
# Set the password for the device
def set_password(value: int):
    # Send 8, 0, 4, 2, i, (SUP : Puis 3* 2 charactère du mdp = 6 char)
    return

# UNTESTED
# Unlock the device with the password
def unlock_password(value: int):
    # Send 7, 0, 5, 2, (SUP : Puis 3* 2 charactère du mdp = 6 char)
    return

# Set the color of a pixel
def set_pixel(x, y, color):
    
    # Convert to int if string
    try:
        x = int(x)
        y = int(y)
    except ValueError as e:
        raise ValueError(f"Invalid parameter type: {e}")
    
    header = bytes.fromhex("0a00050100")                            # Header to write pixel
    color = bytes.fromhex(color)                                    # RGB
    pos = bytes.fromhex(int2hex(x) + int2hex(y))                    # Position
    return header + color + pos

def get_char_file(char):
    
    if char == "!":
        return "font/generated/bang.png"
    elif char == ".":
        return "font/generated/point.png"
    elif char == " ":
        return "font/generated/space.png"
    elif char == "'":
        return "font/generated/apostrophe.png"
    elif char == "-":
        return "font/generated/dash.png"
    elif char == "_":
        return "font/generated/underscore.png"
    elif char == "/":
        return "font/generated/slash.png"
    elif char == "\\":
        return "font/generated/backslash.png"
    elif char == "|":
        return "font/generated/pipe.png"
    elif char == ":":
        return "font/generated/colon.png"
    else:
        return "font/generated/" + char + ".png"

# Encode the text to display
def encode_text(text, color="ffffff"):
    
    # Convert the text to lowercase
    text = text.lower()
    
    # For each character, generate the hex string
    characters = ""
    for char in text:
        characters += "80"      # ???
        characters += color     # RGB color
        characters += "0a10"    # ???
        characters += logic_reverse_bits_order(switch_endian(invert_frames(charimg_to_hex_string(get_char_file(char)))))

    return characters.lower()

def send_text(text, rainbow_mode=0, animation=0, save_slot=1, speed=80, color="ffffff"):
    """
    Send a text to the device and save it in the EEPROM with configurable parameters.

    Parameters:
        text (str): The text to be sent.
        rainbow_mode (int): Rainbow mode (0 for disabled, 2-9 for enabled). Default is 0.
        animation (int): Animation type (0 for static, 1-2, 5-7 to animate. DO NOT USE 3-4). Default is 0.
        save_slot (int): Save slot (e.g., 1). Default is 1.
        speed (int): Speed of the animation (0-255). Default is 80.

    Returns:
        bytes: The formatted bytes to send to the device.
    """
    # Ensure all numeric parameters are integers
    try:
        rainbow_mode = int(rainbow_mode)
        animation = int(animation)
        save_slot = int(save_slot)
        speed = int(speed)
    except ValueError as e:
        raise ValueError(f"Invalid parameter type: {e}")
    
    # Ensure input parameters are within the valid range
    if not 0 <= rainbow_mode <= 9:
        raise ValueError("Rainbow mode must be between 0 and 9")
    if not (0 <= animation <= 2 or 5 <= animation <= 7):
        raise ValueError("Animation must be between 0 and 2 or 5 and 7")
    if not 1 <= save_slot <= 10:
        raise ValueError("Save slot must be between 1 and 10")
    if not 0 <= speed <= 255:
        raise ValueError("Speed must be between 0 and 255")
    if not 1 <= len(text) <= 100:
        raise ValueError("Text length must be between 1 and 100 characters")

    # Generate the header
    header_1 = switch_endian(hex(0x1D + len(text) * 0x26)[2:].zfill(4))
    header_2 = "000100"
    header_3 = switch_endian(hex(0xE + len(text) * 0x26)[2:].zfill(4))
    header_4 = "0000"
    header = header_1 + header_2 + header_3 + header_4

    # Convert parameters to hexadecimal format
    save_slot_hex = hex(save_slot)[2:].zfill(4)         # Convert save slot to hex
    number_of_characters = int2hex(len(text))           # Number of characters

    properties = "000101"                               # Header for properties
    animation_hex = hex(animation)[2:].zfill(2)         # Convert animation to hex
    speed_hex = hex(speed)[2:].zfill(2)                 # Convert speed to hex
    rainbow_mode_hex = hex(rainbow_mode)[2:].zfill(2)   # Convert rainbow_mode to hex
    filler = "ffffff00000000"                           # Placeholder filler
    properties += animation_hex + speed_hex + rainbow_mode_hex + filler

    characters = encode_text(text, color)
    checksum = CRC32_checksum(number_of_characters + properties + characters)
    #print("[DEBUG] Sending data: " + header + checksum + save_slot_hex + number_of_characters + properties + characters)

    return bytes.fromhex(header + checksum + save_slot_hex + number_of_characters + properties + characters)

# Set the screen to display an PNG image (path)
# Only for a short time ?
def set_screen(path):
    header = bytes.fromhex("091200000000120000")

    payload = image_to_rgb_string(path)
    
    data = header + bytes.fromhex(payload)
    
    return data

# Send an GIF animation to the device (hex)
def send_animation_hex(gif_hex):
    CST = "030000"
    checksum = CRC32_checksum(gif_hex)
    sizegif = get_frame_size(gif_hex, 8)
    slot = "0201" # Number of images on the left, slot on the right ?
    totalsize = get_frame_size("FFFF" + CST + sizegif + checksum + slot + gif_hex, 4)
    
    return bytes.fromhex(totalsize + CST + sizegif + checksum + slot + gif_hex)

# Send an GIF animation to the device (path)
def send_animation_path(path):
    with open(path, "rb") as f:
        gif_hex = f.read().hex()
    
    return send_animation_hex(gif_hex)

# Send an GIF animation to the device (path or hex)
def send_animation(path_or_hex):
    if path_or_hex.endswith(".gif"):
        return send_animation_path(path_or_hex)
    else:
        return send_animation_hex(path_or_hex)

# UNTESTED
# Delete a screen of the EEPROM
def delete_screen(n):
    header = bytes.fromhex("070002010100")
    return header + bytes.fromhex(int2hex(n))

# UNTESTED
# Change the save slot position ???
def set_save_position(n):
    header = bytes.fromhex("070008800100")
    return header + bytes.fromhex(int2hex(n))
