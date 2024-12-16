from PIL import Image
import os
import string

def generate_names(index):
    """
    Génère des noms de fichiers : a.png, b.png, ..., z.png, puis 0.png, 1.png, ...
    
    :param index: Index du fichier actuel
    :return: Nom du fichier
    """
    letters = list(string.ascii_lowercase)  # a, b, c, ..., z
    digits = [str(i) for i in range(10)]    # 0, 1, 2, ..., 9
    custom_names = letters + digits         # Combine lettres et chiffres
    if index < len(custom_names):
        return f"{custom_names[index]}.png"
    return f"{index}.png"  # Par défaut, utilise l'index numérique si épuisé

def decouper_image(image_path, output_folder, width=9, height=16, offset_x=1, offset_y=0):
    """
    Découpe une image en rectangles de taille spécifiée avec un offset donné.

    :param image_path: Chemin vers l'image d'origine
    :param output_folder: Dossier où sauvegarder les rectangles
    :param width: Largeur des rectangles
    :param height: Hauteur des rectangles
    :param offset_x: Décalage horizontal entre les rectangles
    :param offset_y: Décalage vertical entre les rectangles
    """
    # Charger l'image
    image = Image.open(image_path)
    image_width, image_height = image.size
    
    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Initialiser les indices pour les morceaux
    index = 0
    
    # Parcourir l'image avec les offsets
    for y in range(0, image_height - height + 1, height + offset_y):
        for x in range(0, image_width - width + 1, width + offset_x):
            # Découper la partie de l'image
            box = (x, y, x + width, y + height)
            cropped_image = image.crop(box)
            
            # Générer le nom du fichier
            file_name = generate_names(index)
            output_path = os.path.join(output_folder, file_name)
            
            # Sauvegarder le rectangle découpé
            cropped_image.save(output_path)
            print(f"Rectangle sauvegardé : {output_path}")
            
            index += 1

if __name__ == "__main__":
    image_path = "all.png"
    output_folder = "generated"
    decouper_image(image_path, output_folder)