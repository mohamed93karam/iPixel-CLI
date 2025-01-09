import binascii
from bit_tools import *
from img_2_pix import image_to_rgb_string
from img_2_pix import charimg_to_hex_string

address = "4B:1E:2E:35:73:A3"

# Set the clock mode
def set_clock_mode(value: int = 1):
    # Sending {11, 0, 6, 1}, then clock to display (then Years, Month, Days, "weekOfDate" ?)
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
    
# Set the screen orientation to upside down
def set_upside_down():
    # Send {5, 0, 6, ByteCompanionObject.MIN_VALUE ???, 0}
    return

# Wipe the EEPROM (Reset)
def clear():
    # Envoie de 4, 0, 3, + byte companion code (0x80 = 128)
    return bytes.fromhex("04000380")

# Set the device brightness
# Value must be between 0 and 100
def set_brightness(value: int):
    # Send 5, 0, 4, + byte companion code (0x80 = 128) + Brightness (0 à 100)
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
def encode_text(text):
    
    # Convert the text to lowercase
    text = text.lower()
    
    # For each character, generate the hex string
    characters = ""
    for char in text:
        characters += "80"      # ???
        characters += "ffffff"  # Color
        characters += "0a10"    # ???
        characters += logic_reverse_bits_order(switch_endian(invert_frames(charimg_to_hex_string(get_char_file(char)))))

    return characters.lower()

# Send a text to the device and save it in the EEPROM
def send_text(text):
    header_1 = switch_endian(hex(0x1D + len(text) * 0x26)[2:].zfill(4))
    header_2 = "000100"
    header_3 = switch_endian(hex(0xE + len(text) * 0x26)[2:].zfill(4))
    header_4 = "0000"
    header = header_1 + header_2 + header_3 + header_4
    
    save_slot = "0001"                                          # Save slot : 0065 temporaire
    number_of_characters = int2hex(len(text))                   # Number of characters
    
    properties = "000101"                                       # header
    animation = "01"                                            # 00 static, 01 right to left, 02 right to left, 05 blink, 06 breath, 07 Snowfall
    speed = "50"                                                # Speed
    rainbow_mode = "09"                                         # 00 disabled, from 02 to 09 = enabled
    filler = "ffffff00000000"                                   # Useless ?
    properties += animation + speed + rainbow_mode + filler
    
    characters = encode_text(text)
    
    checksum = CRC32_checksum(number_of_characters + properties + characters)
    
    print("[DEBUG] Sending data : " + header + checksum + save_slot + number_of_characters + properties + characters)
    
    return bytes.fromhex(header + checksum + save_slot + number_of_characters + properties + characters)

# Show a PNG only for a short period of time
def set_screen():
    header = bytes.fromhex("091200000000120000")
    payload = ""
    
    # Show a blank screen
    # for i in range(16*96):
    #     payload += "ffffff"
    
    payload = image_to_rgb_string("testAAL.png")
    
    data = header + bytes.fromhex(payload)
    
    return data

# Send an GIF animation to the device
def send_animation(gif_hex):
    CST = "030000"
    checksum = CRC32_checksum(gif_hex)
    sizegif = get_frame_size(gif_hex, 8)
    slot = "0201" # Number of images on the left, slot on the right ?
    totalsize = get_frame_size("FFFF" + CST + sizegif + checksum + slot + gif_hex, 4)
    
    return bytes.fromhex(totalsize + CST + sizegif + checksum + slot + gif_hex)

# UNTESTED
# Delete a screen from the EEPROM
def delete_screen(n):
    header = bytes.fromhex("070002010100")
    return header + bytes.fromhex(int2hex(n))

# UNTESTED
# Change the save slot position ???
def set_save_position(n):
    header = bytes.fromhex("070008800100")
    return header + bytes.fromhex(int2hex(n))
