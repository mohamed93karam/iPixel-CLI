import asyncio
import binascii
from bleak import BleakClient
from crccheck.crc import Crc8Maxim
from img_2_pix import image_to_rgb_string
from img_2_pix import charimg_to_hex_string

address = "4B:1E:2E:35:73:A3"

# Prend un int en chaine de caractère en hexadécimal sur 2 caractères
def int2hex(n: int) -> str:
    return hex(n)[2:].zfill(2)

def clock(value: int = 1):
    # Envoie de {11, 0, 6, 1} puis choix de la clock, puis Année, Mois, Jour, "weekOfDate".
    header = bytes.fromhex("0b000601")
    parameter = bytes.fromhex(int2hex(value))
    end = bytes.fromhex("0100e80c0706")

    return header + parameter + end

# Set the DIY Fun Mode (Mode de dessin)
# Screen will not be saved in the EEPROM
def setDIYFunMode(value):
    # Envoie de {5, 0, 4, 1, 1}
    data = bytes.fromhex("05000401")
    if value:
        data += bytes.fromhex("01")
    else:
        data += bytes.fromhex("00")
    return data
    
# UNTESTED
def upsideDown():
    # Envoie de {5, 0, 6, ByteCompanionObject.MIN_VALUE ???, 0}
    return

def clear():
    # Envoie de 4, 0, 3, + byte companion code (0x80 = 128)
    return bytes.fromhex("04000380")

def luminosity(value: int):
    # Envoie de 5, 0, 4, + byte companion code (0x80 = 128) + Luminosité (0 à 100)
    header = bytes.fromhex("05000480")
    parameter = bytes.fromhex(str(value).zfill(2))

    return header + parameter
    
# UNTESTED : Sort tout droit de la décompilation, potentiellement dangereux
def setPassword(value: int):
    # Envoie de 8, 0, 4, 2, i, (SUP : Puis 3* 2 charactère du mdp = 6 char)
    return

def unlockPassword(value: int):
    # Envoie de 7, 0, 5, 2, (SUP : Puis 3* 2 charactère du mdp = 6 char)
    return

def setPixel(x, y, color):
    header = bytes.fromhex("0a00050100")                            # Header to write pixel
    color = bytes.fromhex(color)                                    # RGB
    pos = bytes.fromhex(int2hex(x) + int2hex(y))                    # Position
    return header + color + pos

def test():
    
    # print_character_from_hex(logic_reverse_bits_order(switch_endian(invert_frames("07000600060006000600fe0086018601860186018601860186018601fe000000"))))
    # print(charimg_to_hex_string("b.png"))
    # print_character_from_hex(charimg_to_hex_string("b.png"))
    #encode_char("b.png")
    
    return bytes.fromhex(test)

# Switch Endian
def switch_endian(hex_string: str) -> str:
    if len(hex_string) % 2 != 0:
        raise ValueError("La longueur de la chaîne hexadécimale doit être paire.")

    octets = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
    octets.reverse()
    return ''.join(octets)

# Inverse l'ordre de trames de 2 octets
def invert_frames(hex_string: str) -> str:
    # Split the string into 4 characters
    frames = [hex_string[i:i+4] for i in range(0, len(hex_string), 4)]
    frames.reverse()
    return ''.join(frames)

# Applique la logique NOT sur une chaine hexadécimale
def logic_not_hex(hex_string: str) -> str:
    # Split the string into 2 characters
    octets = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
    # Apply the NOT logic on each character
    inverted = [f"{~int(octet, 16) & 0xFF:02x}" for octet in octets]
    return ''.join(inverted)

def reverse_bits_16(n):
    """Inverse les bits d'un entier 16 bits."""
    n = ((n & 0xFF00) >> 8) | ((n & 0x00FF) << 8)  # Échange des 8 bits de poids fort/faible
    n = ((n & 0xF0F0) >> 4) | ((n & 0x0F0F) << 4)  # Échange des groupes de 4 bits
    n = ((n & 0xCCCC) >> 2) | ((n & 0x3333) << 2)  # Échange des groupes de 2 bits
    n = ((n & 0xAAAA) >> 1) | ((n & 0x5555) << 1)  # Échange des bits individuels
    return n

def logic_reverse_bits_order(hex_string):
    """
    Prend une chaîne hexadécimale, inverse les bits de chaque paquet de 2 octets,
    et retourne une nouvelle chaîne hexadécimale.
    """
    # Vérification que la longueur de la chaîne est paire
    if len(hex_string) % 4 != 0:
        raise ValueError("La chaîne hexadécimale doit avoir une longueur multiple de 4 (2 octets).")
    
    result = []
    
    # Parcours de la chaîne par paquets de 4 caractères hexadécimaux (2 octets)
    for i in range(0, len(hex_string), 4):
        chunk = hex_string[i:i+4]  # Extraire 2 octets (4 caractères hex)
        value = int(chunk, 16)     # Convertir en entier base 16
        reversed_value = reverse_bits_16(value)  # Inverser les bits
        result.append(f"{reversed_value:04X}")   # Ajouter à la liste en format hexadécimal
    
    return "".join(result)  # Retourner la chaîne hex finale

# Calcul le checksum CRC32 de données (bytes)
def CRC32_checksum(data):
    # Calculer naïvement le CRC32
    calculated_crc = binascii.crc32(bytes.fromhex(data)) & 0xFFFFFFFF
    calculated_crc_hex = f"{calculated_crc:08x}"
    # Renvoyer le CRC32 avec Switch Endian.
    return switch_endian(calculated_crc_hex)

# Affichage lisible par un humain des trames
def print_hex(hex_string: str):
    octets = [hex_string[i:i+4] for i in range(0, len(hex_string), 4)]
    print(' '.join(octets))

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

# Encodage d'un texte en hexadécimal
def encode_text(text):
    
    # Convertit le texte en minuscules
    text = text.lower()
    
    # Pour chaque caractère, encode le caractère en hexadécimal
    characters = ""
    for char in text:
        characters += "80"      # ???
        characters += "ffffff"  # Color
        characters += "0a10"    # ???
        characters += logic_reverse_bits_order(switch_endian(invert_frames(charimg_to_hex_string("font/generated/" + char + ".png"))))

    return characters.lower()

# Envoi du texte sur l'affichage ET sauvegarde dans l'EEPROM
def sendText(text):
    header_1 = hex(0x1D + len(text) * 0x26)[2:]
    header_2 = "00000100"
    header_3 = hex(0xE + len(text) * 0x26)[2:]
    header_4 = "000000"
    header = header_1 + header_2 + header_3 + header_4
    
    save_slot = "0001"                                          # Save slot
    
    number_of_characters = int2hex(len(text))                   # Number of characters
    
    properties = "000101005000ffffff00000000"                 # Different properties : Colors, speed
    
    characters = encode_text(text)
    
    checksum = CRC32_checksum(number_of_characters + properties + characters)
    
    print("[DEBUG] Sending data : " + header + checksum + save_slot + number_of_characters + properties + characters)
    
    return bytes.fromhex(header + checksum + save_slot + number_of_characters + properties + characters)

def setScreen():
    # Les couleurs sont mises à la suite, à partir du HEADER, une couleur = 3 octets eg White = FFFFFF
    # Affichage que pdt un cours instant... ???
    header = bytes.fromhex("091200000000120000")
    payload = ""
    
    # Affichage d'un écran blanc
    # for i in range(16*96):
    #     payload += "ffffff"
    
    payload = image_to_rgb_string("testAAL.png") # Après test, l'utilisation d'un filtre linéaire ou sans filtre dépend des logos...
    
    data = header + bytes.fromhex(payload)
    
    return data

# UNTESTED
# Permet de supprimer un écran.
def delete_screen(n):
    header = bytes.fromhex("070002010100")
    return header + bytes.fromhex(int2hex(n))

# UNTESTED
# Permet de changer la position de la sauvegarde pour l'écran qui sera affiché ? (Prefix d'un écran)
# Récupérer pour l'affichage d'un caractère.
def set_save_position(n):
    header = bytes.fromhex("070008800100")
    return header + bytes.fromhex(int2hex(n))

async def runner(address):
    async with BleakClient(address) as client:
        
        #data = clock(7)
        #data = setDIYFunMode(True)
        #data = setPixel(95, 15, "ffffff") # X puis Y
        #data = clear()
        #data = set_save_position(0)
        #data = setScreen()
        #data = test()
        #data = luminosity(0)
        data = sendText("TEST")
        
        crcinst = Crc8Maxim()
        crcinst.process(data)
        model_number = await client.write_gatt_char("0000fa02-0000-1000-8000-00805f9b34fb", data + crcinst.finalbytes())


if __name__ == "__main__":
    asyncio.run(runner(address))