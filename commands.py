import datetime
from bit_tools import *
from img_2_pix import image_to_rgb_string, charimg_to_hex_string

import requests
import json

# Utility functions
def to_bool(value):
    """Convert a value to a boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in {"true", "1", "yes"}:
        return True
    if isinstance(value, str) and value.lower() in {"false", "0", "no"}:
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def to_int(value, name="parameter"):
    """Convert a value to an integer."""
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Invalid integer value for {name}: {value}")


def int_to_hex(n):
    """Convert an integer to a 2-character hexadecimal string."""
    return f"{n:02x}"


def validate_range(value, min_val, max_val, name):
    """Validate that a value is within a specific range."""
    if not min_val <= value <= max_val:
        raise ValueError(f"{name} must be between {min_val} and {max_val}")


# Text encoding
def get_char_file(char):
    """Get the file path for a character."""
    special_chars = {
        "!": "bang", ".": "point", " ": "space", "'": "apostrophe",
        "-": "dash", "_": "underscore", "/": "slash", "\\": "backslash",
        "|": "pipe", ":": "colon"
    }
    return f"font/generated/{special_chars.get(char, char)}.png"


def encode_text(text, color="ffffff"):
    """Encode text to be displayed on the device."""
    return "".join(
        "80" + color + "0a10" + logic_reverse_bits_order(
            switch_endian(invert_frames(charimg_to_hex_string(get_char_file(char))))
        ) for char in text.lower()
    ).lower()

# Commands
def set_clock_mode(style=1, date="", show_date=True, format_24=True):
    """Set the clock mode of the device."""
    style = to_int(style, "style")
    show_date = to_bool(show_date)
    format_24 = to_bool(format_24)

    # Process date
    if not date:
        now = datetime.datetime.now()
        day, month, year = now.day, now.month, now.year % 100
        day_of_week = now.weekday() + 1
    else:
        try:
            day, month, year = map(int, date.split("/"))
            day_of_week = datetime.datetime(year, month, day).weekday() + 1
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid date format: {e}")

    # Validate ranges
    validate_range(style, 0, 8, "Clock mode")
    validate_range(day_of_week, 1, 7, "Day of week")
    validate_range(month, 1, 12, "Month")
    validate_range(day, 1, 31, "Day")
    validate_range(year, 0, 99, "Year")

    # Build byte sequence
    header = bytes.fromhex("0b000601")
    params = bytes.fromhex(int_to_hex(style) + ("01" if format_24 else "00") + ("01" if show_date else "00"))
    date_bytes = bytes.fromhex(int_to_hex(year) + int_to_hex(month) + int_to_hex(day) + int_to_hex(day_of_week))

    return header + params + date_bytes

def set_time(hour=None, minute=None, second=None):
    """Set the time of the device. If no time is provided, it uses the current system time."""
    if hour is None or minute is None or second is None:
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second
    hour = to_int(hour, "hour")
    minute = to_int(minute, "minute")
    second = to_int(second, "second")
    
    validate_range(hour, 0, 23, "Hour")
    validate_range(minute, 0, 59, "Minute")
    validate_range(second, 0, 59, "Second")
    
    return bytes.fromhex("08000180") + bytes([hour, minute, second]) + bytes.fromhex("00")

def set_fun_mode(value=False):
    """Set the DIY Fun Mode (Drawing Mode)."""
    return bytes.fromhex("05000401") + bytes.fromhex("01" if to_bool(value) else "00")


def set_orientation(orientation=0):
    """Set the orientation of the device."""
    orientation = to_int(orientation, "orientation")
    validate_range(orientation, 0, 2, "Orientation")
    return bytes.fromhex("05000680") + bytes.fromhex(int_to_hex(orientation))


def clear():
    """Clear the EEPROM."""
    return bytes.fromhex("04000380")


def set_brightness(value):
    """Set the brightness of the device."""
    value = to_int(value, "brightness")
    validate_range(value, 0, 100, "Brightness")
    return bytes.fromhex("05000480") + bytes.fromhex(int_to_hex(value))


def set_speed(value):
    """Set the speed of the device. (Broken)"""
    value = to_int(value, "speed")
    validate_range(value, 0, 100, "Speed")
    return bytes.fromhex("050003") + bytes.fromhex(int_to_hex(value))


def set_pixel(x, y, color):
    """Set the color of a specific pixel."""
    x, y = map(to_int, [x, y])
    return bytes.fromhex("0a00050100") + bytes.fromhex(color) + bytes.fromhex(int_to_hex(x) + int_to_hex(y))


def send_text(text, rainbow_mode=0, animation=0, save_slot=1, speed=80, color="ffffff"):
    """Send a text to the device with configurable parameters."""
    if len(text) == 0:
        text = get_text_from_url("https://script.google.com/a/macros/alpinrad.com/s/AKfycbyyoOmdU3cayVD9urQGvpj_k_3hWxq-QmFA-Ksxyaz_k772vwTf6O74Ez6VohWrCk4/exec?happyhour=true")
        
    rainbow_mode = to_int(rainbow_mode, "rainbow mode")
    animation = to_int(animation, "animation")
    save_slot = to_int(save_slot, "save slot")
    speed = to_int(speed, "speed")
    
    for param, min_val, max_val, name in [
        (rainbow_mode, 0, 9, "Rainbow mode"),
        (animation, 0, 7, "Animation"),
        (save_slot, 1, 10, "Save slot"),
        (speed, 0, 100, "Speed"),
        (len(text), 1, 100, "Text length")
    ]:
        validate_range(param, min_val, max_val, name)

    if animation == 3 or animation == 4:
        raise ValueError("Invalid animation for text display")

    header_1 = switch_endian(hex(0x1D + len(text) * 0x26)[2:].zfill(4))
    header_2 = "000100"
    header_3 = switch_endian(hex(0xE + len(text) * 0x26)[2:].zfill(4))
    header_4 = "0000"
    header = header_1 + header_2 + header_3 + header_4
    
    save_slot_hex = hex(save_slot)[2:].zfill(4)       # Convert save slot to hex
    number_of_characters = int_to_hex(len(text))      # Number of characters
    
    properties = f"000101{int_to_hex(animation)}{int_to_hex(speed)}{int_to_hex(rainbow_mode)}ffffff00000000"
    characters = encode_text(text, color)
    checksum = CRC32_checksum(number_of_characters + properties + characters)

    return bytes.fromhex(header + checksum + save_slot_hex + number_of_characters + properties + characters)


def set_screen(path):
    """Set the screen to display an image."""
    return bytes.fromhex("091200000000120000") + bytes.fromhex(image_to_rgb_string(path))


def send_animation(path_or_hex):
    """Send a GIF animation to the device."""
    if path_or_hex.endswith(".gif"):
        with open(path_or_hex, "rb") as f:
            gif_hex = f.read().hex()
    else:
        gif_hex = path_or_hex

    checksum = CRC32_checksum(gif_hex)
    size = get_frame_size(gif_hex, 8)
    return bytes.fromhex(f"{get_frame_size('FFFF030000' + size + checksum + '0201' + gif_hex, 4)}030000{size}{checksum}0201{gif_hex}")


def delete_screen(n):
    """Delete a screen from the EEPROM."""
    return bytes.fromhex("070002010100") + bytes.fromhex(int_to_hex(to_int(n, "screen index")))

def get_text_from_url(url: str) -> str | None:
    """
    Sends a GET request to a URL, parses the JSON response, and returns the 'text' field.

    Args:
        url: The URL to send the request to.

    Returns:
        The text from the JSON response or None if an error occurs.
    """
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # Parse the JSON response from the request
        data = response.json()

        # Extract and return the value of the 'text' key
        return data.get("code")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred with the request: {e}")
        return None
    except json.JSONDecodeError:
        print("Failed to parse JSON response.")
        return None

