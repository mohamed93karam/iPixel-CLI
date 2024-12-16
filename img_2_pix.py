from PIL import Image

def image_to_rgb_string(image_path):
    try:
        # Ouvre l'image
        img = Image.open(image_path)
        # S'assure que l'image est en mode RGB
        img = img.convert('RGB')
        
        # Initialise la chaine qui contiendra les pixels
        pixel_string = ""
        
        # Récupère la taille de l'image
        width, height = img.size
        
        # Parcourt chaque pixel ligne par ligne
        for y in range(height):
            for x in range(width):
                r, g, b = img.getpixel((x, y))
                # Convertit les valeurs RGB en hexadécimal sur 2 caractères chacun
                pixel_string += f"{r:02x}{g:02x}{b:02x}"
        
        return pixel_string
    except Exception as e:
        print(f"Erreur : {e}")
        return None

if __name__ == "__main__":
    image_path = input("Entrez le chemin de l'image : ")
    result = image_to_rgb_string(image_path)
    if result:
        print("La chaine de caractères de l'image :")
        print(result)

# Create an hex frame from a 9x16 character img
# For 16 lines, convert the first 9 pixels to a 2 bytes hex value
# bit shift the 9 bits to the left by 7.
# if the pixel is white, add 1 bit, else add 0
def charimg_to_hex_string(image_path):
    """
    Convertit une image 9x16 en une string de valeurs hexadécimales.
    Chaque ligne est codée sur 2 octets (16 bits) :
    - Les 9 bits de poids fort représentent les pixels (1 pour coloré, 0 pour noir).
    - Les 7 bits de poids faible sont inutilisés.
    """
    # Charger l'image et la convertir en mode L (niveau de gris)
    img = Image.open(image_path).convert("L")

    # Vérification de la taille de l'image
    if img.size != (9, 16):
        raise ValueError("L'image doit être de taille 9x16 pixels.")

    hex_string = ""

    # Parcourir chaque ligne (hauteur)
    for y in range(16):
        line_value = 0

        # Parcourir chaque colonne (largeur) pour construire les 9 bits
        for x in range(9):
            pixel = img.getpixel((x, y))
            if pixel > 0:  # Si le pixel est coloré (différent de noir)
                line_value |= (1 << (15 - x))  # Déplacer les bits pour les 9 bits de poids fort

        # Convertir la valeur de la ligne en hexadécimal et l'ajouter à la chaîne
        hex_string += f"{line_value:04X}"

    return hex_string