import binascii
from crccheck.crc import Crc8Maxim

# Invert the frames of a hex string
def invert_frames(hex_string: str) -> str:
    # Split the string into 4 characters
    frames = [hex_string[i:i+4] for i in range(0, len(hex_string), 4)]
    frames.reverse()
    return ''.join(frames)

# Switch the endian of a hexadecimal string
def switch_endian(hex_string: str) -> str:
    if len(hex_string) % 2 != 0:
        raise ValueError("La longueur de la chaîne hexadécimale doit être paire.")

    octets = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
    octets.reverse()
    return ''.join(octets)

# Apply the NOT logic on a hexadecimal string
def logic_not_hex(hex_string: str) -> str:
    # Split the string into 2 characters
    octets = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
    # Apply the NOT logic on each character
    inverted = [f"{~int(octet, 16) & 0xFF:02x}" for octet in octets]
    return ''.join(inverted)

def reverse_bits_16(n):
    """Inverse les bits d'un entier 16 bits."""
    n = ((n & 0xFF00) >> 8) | ((n & 0x00FF) << 8)
    n = ((n & 0xF0F0) >> 4) | ((n & 0x0F0F) << 4)
    n = ((n & 0xCCCC) >> 2) | ((n & 0x3333) << 2)
    n = ((n & 0xAAAA) >> 1) | ((n & 0x5555) << 1)
    return n

def logic_reverse_bits_order(hex_string):
    # Check if the length is a multiple of 4 (2 bytes)
    if len(hex_string) % 4 != 0:
        raise ValueError("La chaîne hexadécimale doit avoir une longueur multiple de 4 (2 octets).")
    
    result = []
    
    # For each 4 characters, reverse the bits
    for i in range(0, len(hex_string), 4):
        chunk = hex_string[i:i+4]                   # Extract 4 characters
        value = int(chunk, 16)                      # Convert to integer
        reversed_value = reverse_bits_16(value)     # Reverse the bits
        result.append(f"{reversed_value:04X}")      # Convert back to hex and append
    
    return "".join(result)  # Concatenate the result

def file_to_strhex(file):
    with open(file, "rb") as f:
        return binascii.hexlify(f.read()).decode("utf-8")

def get_frame_size(data, size):
    return switch_endian(hex(len(data) // 2)[2:].zfill(size))

# Process CRC32 checksum for the data
def CRC32_checksum(data):
    # Process the CRC32 checksum
    calculated_crc = binascii.crc32(bytes.fromhex(data)) & 0xFFFFFFFF
    calculated_crc_hex = f"{calculated_crc:08x}"
    # Send the checksum by switching endian
    return switch_endian(calculated_crc_hex)

# DEBUG : Show human readable hex string
def print_hex(hex_string: str):
    octets = [hex_string[i:i+4] for i in range(0, len(hex_string), 4)]
    print(' '.join(octets))

# DEBUG (unused)
def print_character_from_hex(hex_string: str):
    # 9*16 pixels grid, 1 is for ON, 0 is for OFF
    # For each 4 hex characters, print a line in binary
    for i in range(0, len(hex_string), 4):
        line = bin(int(hex_string[i:i+4], 16))[2:].zfill(16)
        for j in range(0, 16, 1):
            if line[j] == "0":
                print("  ", end="")
            else:
                print("##", end="")
        print("")