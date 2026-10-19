import customtkinter as ctk
import unicodedata
import numpy as np
from math import ceil

# ========== Configuration de l'interface ==========
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# ========== Styles Avancés (préparer palette) ==========
ACCENT_GRADIENT = ("#6366f1", "#8b5cf6")  # Dégradé violet
NEON_EFFECT = "#06b6d4"                   # Effet néon cyan
DARK_BG = "#0f172a"                       # Fond sombre
CARD_COLOR = "#1e293b"                    # Couleur des cartes

# ========== Fonctions de chiffrement ==========

   #pour polybe et playfair
def supp_accents_miniscules_ponctuations(message):
    mess = unicodedata.normalize('NFD', message)
    result = ""
    for let in mess:
        if ord(let) in range(97, 123):
            let = chr(ord(let) - 32)
        if ord(let) in range(65, 91):
            result += let
    return result.replace("J", "I")

  #pour hill (ne pas remplacer les j par i)
def nettoyer_texte(texte):
    texte = unicodedata.normalize('NFD', texte)
    resultat = []
    for caractere in texte:
        if ord(caractere) in range(65, 91):
            resultat.append(caractere)
        elif ord(caractere) in range(97, 123):
            resultat.append(chr(ord(caractere) - 32))
    return ''.join(resultat)

# ========== Chiffrement Polybe ==========
grille = [['A','B','C','D','E'],
          ['F','G','H','I','K'],
          ['L','M','N','O','P'],
          ['Q','R','S','T','U'],
          ['V','W','X','Y','Z']]

def chiffrementPolybe(mess):
    mess = supp_accents_miniscules_ponctuations(mess)
    c = ""
    for let in mess:
        for i, ligne in enumerate(grille):#enumerate pour l'indice
            for j, elem in enumerate(ligne):
                if elem == let:
                    c += str(i+1) + str(j+1) + " "
    return c.strip()#retirer le dernier espace

def dechiffrementPolybe(mess):
    p = ""
    mess = "".join(mess.split())#enlever les epaces
    for index in range(0, len(mess), 2):
        coord = mess[index:index+2]
        if len(coord) == 2 and coord.isdigit():
            i, j = int(coord[0]), int(coord[1])
            if 1 <= i <= 5 and 1 <= j <= 5:
                p += grille[i-1][j-1]
            else:
                p += "?"
        else:
            p += "?"
    return p

# ========== Chiffrement Playfair ==========

 #construire la grille
def create_playfair_square(key):
    key = supp_accents_miniscules_ponctuations(key) + "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    key = "".join(dict.fromkeys(key))#supprimer les doublons
    return [list(key[i:i+5]) for i in range(0, 25, 5)]#grille 5*5

 #retourner les coordonnées d'un char dans la grille
def find_location(grid, char):
    for i in range(5):
        for j in range(5):
            if grid[i][j] == char:
                return i, j
    return None

#construire les bloc de 2 carac
def create_digrams(message):
    message = supp_accents_miniscules_ponctuations(message)
    digrams = []
    i = 0
    while i < len(message):
        if i + 1 < len(message) and message[i] == message[i+1]:
            digrams.append(message[i] + 'X')
            i += 1
        elif i + 1 < len(message):
            digrams.append(message[i] + message[i+1])
            i += 2
        else:
            digrams.append(message[i] + 'X')
            i += 1
    return digrams

def playfair_encrypt(message, key):
    grid = create_playfair_square(key)
    digrams = create_digrams(message)
    ciphertext = ""
    for digram in digrams:
        row1, col1 = find_location(grid, digram[0])
        row2, col2 = find_location(grid, digram[1])
        if row1 == row2:#meme ligne
            ciphertext += grid[row1][(col1 + 1) % 5] + grid[row2][(col2 + 1) % 5]
        elif col1 == col2:#meme colonne
            ciphertext += grid[(row1 + 1) % 5][col1] + grid[(row2 + 1) % 5][col2]
        else:#rectangle
            ciphertext += grid[row1][col2] + grid[row2][col1]
    return ciphertext

def playfair_decrypt(ciphertext, key):
    grid = create_playfair_square(key)
    digrams = [ciphertext[i:i+2] for i in range(0, len(ciphertext), 2)]
    plaintext = ""
    for digram in digrams:
        row1, col1 = find_location(grid, digram[0])
        row2, col2 = find_location(grid, digram[1])
        if row1 is None or row2 is None:
            return "Erreur : caractère inconnu"
        if row1 == row2:#a gauche
            plaintext += grid[row1][(col1 - 1) % 5] + grid[row2][(col2 - 1) % 5]
        elif col1 == col2:#au dessus
            plaintext += grid[(row1 - 1) % 5][col1] + grid[(row2 - 1) % 5][col2]
        else:#echanger les col
            plaintext += grid[row1][col2] + grid[row2][col1]
    return plaintext.replace('X', '')#supprimer les x ajoutés

# ========== Chiffrement Hill ==========
alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

def chiffrementHill(m, mot, sens):
    mot = nettoyer_texte(mot)
    e = ''
    dim = np.shape(m)[0]
    if len(mot) % dim != 0:#completer avec des x
        r = dim - (len(mot) % dim)
        mot += 'X' * r
    for i in range(0, len(mot), dim):#mul matricielle
        for line in range(0, dim):
            a = 0
            for column in range(0, dim):
                a += round(m[line][column]) * alphabet.index(mot[i + column])
            a = int(a % len(alphabet))
            e += alphabet[a]
    return e

def dechiffrementHill(matrice, message_chiffre):
    message_chiffre = nettoyer_texte(message_chiffre)
    dim = matrice.shape[0]
    
    try:
        det = int(round(np.linalg.det(matrice)))#calcul du DET
        if det == 0:
            return "Erreur : Matrice non inversible"
        
        inv_mod = pow(det, -1, 26)#calcul inverse modulaire
        matrice_inv = np.linalg.inv(matrice)#inverse de la mat
        matrice_inv = (matrice_inv * det * inv_mod).round().astype(int) % 26#mod 26
        
        return chiffrementHill(matrice_inv, message_chiffre, 'déchiffré')
    except Exception as e:
        return f"Erreur : {str(e)}"

# ========== Chiffrement par Transposition ==========

# retourner l’ordre des colonnes selon le tri alphabétique
def clefChiffrementTranspo(clef):
    return [i for i, _ in sorted(enumerate(clef), key=lambda x: (x[1], x[0]))]#enumerate pour tuples(indice,carac)
                                                                              #puis trier les indices

def chiffrementTranspo(msg, clef):
    msg = supp_accents_miniscules_ponctuations(msg)
    clef = supp_accents_miniscules_ponctuations(clef)

    ordre_colonnes = clefChiffrementTranspo(clef)

    colonnes = len(clef)     #nb col
    lignes = ceil(len(msg) / colonnes) #nb lignes

    # Compléter le message avec X si nécessaire
    msg += 'X' * (lignes * colonnes - len(msg))

    # Créer la matrice ligne par ligne(diviser)
    matrice = [list(msg[i*colonnes:(i+1)*colonnes]) for i in range(lignes)]

    # Réorganiser les colonnes selon l’ordre donné
    matrice_colonnes = []
    for idx in ordre_colonnes:
        col = [ligne[idx] for ligne in matrice]
        matrice_colonnes.append(col)

    # Lire colonne par colonne pour obtenir le texte chiffré(et concaténation)
    msg_code = ''.join([''.join(col) for col in matrice_colonnes])
    return msg_code


def dechiffrementTranspo(ciphertext, clef):
    ciphertext = supp_accents_miniscules_ponctuations(ciphertext)
    clef = supp_accents_miniscules_ponctuations(clef)
    colonnes = len(clef)
    lignes = ceil(len(ciphertext) / colonnes)
    ordre = clefChiffrementTranspo(clef)
    matrice = [[''] * colonnes for _ in range(lignes)]
    index = 0
    for pos in ordre:                 #placer le texte colonne par colonne
        for i in range(lignes):
            if index < len(ciphertext):
                matrice[i][pos] = ciphertext[index]
                index += 1
    texte_clair = "".join(["".join(ligne) for ligne in matrice])#parcourir les lignes
    return texte_clair

# ========== Chiffrement DES ==========


# Tables de permutation 
IP = [58, 50, 42, 34, 26, 18, 10, 2,
      60, 52, 44, 36, 28, 20, 12, 4,
      62, 54, 46, 38, 30, 22, 14, 6,
      64, 56, 48, 40, 32, 24, 16, 8,
      57, 49, 41, 33, 25, 17, 9, 1,
      59, 51, 43, 35, 27, 19, 11, 3,
      61, 53, 45, 37, 29, 21, 13, 5,
      63, 55, 47, 39, 31, 23, 15, 7]

# Permutation finale (inverse de IP)
FP = [40, 8, 48, 16, 56, 24, 64, 32,
      39, 7, 47, 15, 55, 23, 63, 31,
      38, 6, 46, 14, 54, 22, 62, 30,
      37, 5, 45, 13, 53, 21, 61, 29,
      36, 4, 44, 12, 52, 20, 60, 28,
      35, 3, 43, 11, 51, 19, 59, 27,
      34, 2, 42, 10, 50, 18, 58, 26,
      33, 1, 41, 9, 49, 17, 57, 25]

# Table d'expansion E
E = [32, 1, 2, 3, 4, 5,
     4, 5, 6, 7, 8, 9,
     8, 9, 10, 11, 12, 13,
     12, 13, 14, 15, 16, 17,
     16, 17, 18, 19, 20, 21,
     20, 21, 22, 23, 24, 25,
     24, 25, 26, 27, 28, 29,
     28, 29, 30, 31, 32, 1]

# Permutation P
P = [16, 7, 20, 21, 29, 12, 28, 17,
     1, 15, 23, 26, 5, 18, 31, 10,
     2, 8, 24, 14, 32, 27, 3, 9,
     19, 13, 30, 6, 22, 11, 4, 25]

# Permutation PC1 pour la génération des clés
PC1 = [57, 49, 41, 33, 25, 17, 9,
       1, 58, 50, 42, 34, 26, 18,
       10, 2, 59, 51, 43, 35, 27,
       19, 11, 3, 60, 52, 44, 36,
       63, 55, 47, 39, 31, 23, 15,
       7, 62, 54, 46, 38, 30, 22,
       14, 6, 61, 53, 45, 37, 29,
       21, 13, 5, 28, 20, 12, 4]

# Permutation PC2 pour la génération des clés
PC2 = [14, 17, 11, 24, 1, 5,
       3, 28, 15, 6, 21, 10,
       23, 19, 12, 4, 26, 8,
       16, 7, 27, 20, 13, 2,
       41, 52, 31, 37, 47, 55,
       30, 40, 51, 45, 33, 48,
       44, 49, 39, 56, 34, 53,
       46, 42, 50, 36, 29, 32]

# S-boxes complètes 
S_BOX = [
    # S1
    [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
     [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
     [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
     [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],
    
    # S2
    [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
     [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
     [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
     [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]],
    
    # S3
    [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
     [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
     [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
     [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]],
    
    # S4
    [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
     [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
     [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
     [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]],
    
    # S5
    [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
     [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
     [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
     [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]],
    
    # S6
    [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
     [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
     [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
     [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]],
    
    # S7
    [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
     [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
     [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
     [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]],
    
    # S8
    [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
     [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
     [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
     [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]]
]

# Calendrier de décalage standard DES
LEFT_SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

# Fonctions auxiliaires corrigées
def permute(block, table):
    """Applique la permutation au bloc en utilisant la table fournie."""
    return [block[i-1] for i in table] 

def left_shift(block, shifts):
    """Effectue un décalage circulaire à gauche sur le bloc donné (28 bits)."""
    return block[shifts:] + block[:shifts]

def string_to_bits(text):
    """Convertit une chaîne de caractères en liste de bits."""
    result = []
    for char in text:
        # Convertir chaque caractère en sa représentation binaire sur 8 bits
        bits = bin(ord(char))[2:].zfill(8)
        result.extend([int(bit) for bit in bits])
    return result

def bits_to_string(bits):
    """Convertit une liste de bits en chaîne de caractères."""
    result = ""
    # Traiter les bits par groupes de 8
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) == 8:  # S'assurer qu'on a un octet complet
            char_code = int(''.join(map(str, byte)), 2)
            result += chr(char_code)
    return result

def generate_keys(key):
    """Génère les 16 sous-clés de 48 bits à partir de la clé initiale de 64 bits."""
    # Appliquer la permutation PC1
    key = permute(key, PC1)

    # Diviser en moitiés gauche (C) et droite (D) de 28 bits
    C = key[:28]
    D = key[28:]

    sub_keys = []

    for shift in LEFT_SHIFTS:
        # Appliquer le décalage circulaire
        C = left_shift(C, shift)
        D = left_shift(D, shift)

        # Combiner les moitiés
        combined = C + D

        # Appliquer la permutation PC2 pour obtenir la sous-clé de 48 bits
        sub_key = permute(combined, PC2)
        sub_keys.append(sub_key)

    return sub_keys

def f_function(right, subkey):
    """Applique la fonction f (expansion, substitution et permutation) sur la moitié droite."""
    # Expansion E
    expanded = permute(right, E)
    
    # XOR avec la sous-clé
    xored = [e ^ k for e, k in zip(expanded, subkey)]
    
    # Application des S-boxes
    sbox_output = []
    for i in range(8):
        # Extraire 6 bits pour chaque S-box
        block = xored[i*6:(i+1)*6]
        
        # Calculer les indices de ligne et colonne pour la S-box
        row = (block[0] << 1) | block[5]  # Premier et dernier bit forment la ligne
        col = (block[1] << 3) | (block[2] << 2) | (block[3] << 1) | block[4]  # Bits du milieu forment la colonne
        
        # Obtenir la valeur de la S-box
        sbox_value = S_BOX[i][row][col]
        
        # Convertir en 4 bits
        binary = bin(sbox_value)[2:].zfill(4)
        sbox_output.extend([int(bit) for bit in binary])
    
    # Permutation P
    return permute(sbox_output, P)

def encrypt_block(block, subkeys):
    """Chiffre un bloc de 64 bits en utilisant l'algorithme DES."""
    # Permutation initiale
    block = permute(block, IP)
    
    # Diviser en moitiés gauche et droite
    left, right = block[:32], block[32:]
    
    # 16 rounds
    for i in range(16):
        # Sauvegarder l'ancienne moitié droite
        old_right = right
        
        # Appliquer la fonction f
        f_result = f_function(right, subkeys[i])
        
        # Nouvelle moitié droite = ancienne moitié gauche XOR résultat de f
        right = [l ^ f for l, f in zip(left, f_result)]
        
        # Nouvelle moitié gauche = ancienne moitié droite
        left = old_right
    
    # Inverser les moitiés pour la dernière étape (swap)
    combined = right + left
    
    # Permutation finale
    return permute(combined, FP)

def decrypt_block(block, subkeys):
    """Déchiffre un bloc de 64 bits en utilisant l'algorithme DES."""
    # Pour le déchiffrement, on utilise les sous-clés dans l'ordre inverse
    return encrypt_block(block, subkeys[::-1])

def pad_message(bits):
    """Ajoute du padding au message pour qu'il soit un multiple de 64 bits."""
    if len(bits) % 64 == 0:
        return bits  # Pas de padding si déjà un multiple de 64
    padding_length = 64 - (len(bits) % 64)
    return bits + [0] * padding_length

def des_encrypt(plaintext, key):
    """Chiffre le texte en clair avec la clé donnée."""
    # Convertir le texte en bits
    plaintext_bits = string_to_bits(plaintext)
    
    # Ajouter du padding si nécessaire (maintenant correctement)
    padded_bits = pad_message(plaintext_bits)
    
    key_bits = string_to_bits(key)
    subkeys = generate_keys(key_bits)
    
    # Chiffrer chaque bloc de 64 bits
    encrypted_bits = []
    for i in range(0, len(padded_bits), 64):
        block = padded_bits[i:i+64]
        encrypted_block = encrypt_block(block, subkeys)
        encrypted_bits.extend(encrypted_block)
    
    # Convertir le résultat en chaîne binaire
    return ''.join(map(str, encrypted_bits))

def des_decrypt(ciphertext, key):
    """Déchiffre le texte chiffré avec la clé donnée."""
    # Convertir la chaîne binaire en liste de bits
    ciphertext_bits = [int(bit) for bit in ciphertext]
    
    key_bits = string_to_bits(key)
    subkeys = generate_keys(key_bits)
    
    # Déchiffrer chaque bloc de 64 bits
    decrypted_bits = []
    for i in range(0, len(ciphertext_bits), 64):
        block = ciphertext_bits[i:i+64]
        decrypted_block = decrypt_block(block, subkeys)
        decrypted_bits.extend(decrypted_block)
    
    # Convertir les bits déchiffrés en texte
    return bits_to_string(decrypted_bits)












# ========== Interface Graphique ==========
class CryptoApp(ctk.CTk):
    #inits
    def __init__(self):
        super().__init__()
        self.title("Crypto ING3")
        self.geometry("1200x800")
        self.configure(fg_color=DARK_BG)
        self.setup_ui()
        
    #effets gradient et bords arrondis
    def create_gradient_frame(self, parent):
        return ctk.CTkFrame(
            parent,
            border_width=2,
            border_color=ACCENT_GRADIENT[1],
            fg_color=CARD_COLOR,
            corner_radius=15
        )
    
    #UI
    def setup_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=20, fill="x")
        
        ctk.CTkLabel(
            header_frame,
            text="🛡 CRYPTO_ING3",
            font=("Roboto Black", 24),
            text_color=ACCENT_GRADIENT[1]
        ).pack(side="left", padx=20)

        # une tabview avec des onglets
        self.tabview = ctk.CTkTabview(
            self,
            width=1150,
            height=650,
            segmented_button_selected_color=ACCENT_GRADIENT[1],
            segmented_button_selected_hover_color=ACCENT_GRADIENT[0],
            segmented_button_unselected_hover_color=CARD_COLOR,
            corner_radius=15
        )
        self.tabview.pack(padx=20, fill="both", expand=True)

        tabs = ["Polybe", "Playfair", "Transposition", "Hill","DES"]
        for tab in tabs:
            self.tabview.add(tab)
            self.create_tab_content(tab)

    #contenu pour chaque onglet
    def create_tab_content(self, tab_name):
        tab = self.tabview.tab(tab_name)
        
        # Conteneur principal
        main_container = self.create_gradient_frame(tab)
        main_container.pack(pady=10, padx=10, fill="both", expand=True)

        # Section Entrée
        input_frame = self.create_gradient_frame(main_container)
        input_frame.pack(pady=15, padx=15, fill="x")
        
        ctk.CTkLabel(
            input_frame,
            text=f"🔒 {tab_name.upper()} - Entrée",
            font=("Roboto Medium", 16),
            text_color=NEON_EFFECT
        ).pack(pady=5, anchor="w")
        
        entry = ctk.CTkEntry(
            input_frame,
            font=("Roboto Mono", 14),
            height=45,
            border_color=ACCENT_GRADIENT[0],
            placeholder_text="Entrez votre texte ici..."
        )
        entry.pack(pady=10, fill="x", padx=10)

        # Section Clé/Matrice
        key_frame = self.create_gradient_frame(main_container)
        key_frame.pack(pady=15, padx=15, fill="x")
        
        label_text = "🔑 Clé" if tab_name != "Hill" else "🧮 Matrice"
        ctk.CTkLabel(
            key_frame,
            text=label_text,
            font=("Roboto Medium", 16),
            text_color=NEON_EFFECT
        ).pack(pady=5, anchor="w")
        
        key_entry = ctk.CTkEntry(
            key_frame,
            font=("Roboto Mono", 14),
            height=45,
            border_color=ACCENT_GRADIENT[0],
            placeholder_text="Ex: 'SECRET' ou '2 4; 6 8' pour Hill"
        )
        key_entry.pack(pady=10, fill="x", padx=10)

        # Boutons Animés
        btn_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        encrypt_btn = ctk.CTkButton(
            btn_frame,
            text=" Chiffrement ",
            command=lambda: self.process(tab_name, "encrypt"),
            fg_color=ACCENT_GRADIENT,
            hover_color=NEON_EFFECT,
            font=("Roboto Bold", 14),
            corner_radius=10,
            border_width=2,
            border_color=NEON_EFFECT
        )
        
        decrypt_btn = ctk.CTkButton(
            btn_frame,
            text=" Déchiffrement ",
            command=lambda: self.process(tab_name, "decrypt"),
            fg_color=ACCENT_GRADIENT,
            hover_color=NEON_EFFECT,
            font=("Roboto Bold", 14),
            corner_radius=10,
            border_width=2,
            border_color=NEON_EFFECT
        )
        
        encrypt_btn.pack(side="left", padx=20)
        decrypt_btn.pack(side="left", padx=20)

        # Section Résultat
        result_frame = self.create_gradient_frame(main_container)
        result_frame.pack(pady=15, padx=15, fill="both", expand=True)
        
        ctk.CTkLabel(
            result_frame,
            text="📄 Résultat",
            font=("Roboto Medium", 16),
            text_color=NEON_EFFECT
        ).pack(pady=5, anchor="w")
        
        result_text = ctk.CTkTextbox(
            result_frame,
            font=("Roboto Mono", 14),
            wrap="word",
            height=150,
            fg_color="#1e1e2e",
            border_width=2,
            border_color=ACCENT_GRADIENT[0]
        )
        result_text.pack(pady=10, fill="both", expand=True, padx=10)

        # Stockage des références
        setattr(self, f"{tab_name.lower()}_entry", entry)
        setattr(self, f"{tab_name.lower()}_key_entry", key_entry)
        setattr(self, f"{tab_name.lower()}_result", result_text)
        
    #lorsque on appuie sur un boutton process est appellée
    def process(self, method, action):
        try:
            text = getattr(self, f"{method.lower()}_entry").get()
            key = getattr(self, f"{method.lower()}_key_entry").get()
            result = ""
            
            if method == "Polybe":
                result = dechiffrementPolybe(text) if action == "decrypt" else chiffrementPolybe(text)
            
            elif method == "Playfair":
                if not key:
                    raise ValueError("Clé requise pour Playfair")
                if action == "encrypt":
                    result = playfair_encrypt(text, key)
                else:
                    result = playfair_decrypt(text, key)
            
            elif method == "Transposition":
                if not key:
                    raise ValueError("Clé requise pour Transposition")
                if action == "encrypt":
                    result = chiffrementTranspo(text, key)
                else:
                    result = dechiffrementTranspo(text, key)
            
            elif method == "Hill":
                if not key:
                    raise ValueError("Matrice requise pour Hill")
                try:
                    matrix = np.array([list(map(int, row.split())) for row in key.split(';')])
                except:
                    raise ValueError("Format de matrice invalide")
                
                if action == "encrypt":
                    result = chiffrementHill(matrix, text, "encrypt")
                else:
                    result = dechiffrementHill(matrix, text)
                    
            elif method == "DES":

                                    
                if not key:
                    raise ValueError("Clé requise pour DES")
                if action == "encrypt":
                   result = des_encrypt(text, key)
                else:
                   result = des_decrypt(text, key)

            
            
            getattr(self, f"{method.lower()}_result").delete("0.0", "end")
            getattr(self, f"{method.lower()}_result").insert("0.0", result)
        
        except Exception as e:
            self.show_error(str(e))
    
    def show_error(self, message):
        error_window = ctk.CTkToplevel(self)
        error_window.title("🚨 Erreur")
        error_window.geometry("450x200")
        error_window.configure(fg_color="#2e1a1a")
        
        ctk.CTkLabel(
            error_window,
            text="⚠️ ERREUR DE TRAITEMENT",
            font=("Roboto Black", 18),
            text_color="#ef4444"
        ).pack(pady=10)
        
        ctk.CTkLabel(
            error_window,
            text=message,
            font=("Roboto", 14),
            wraplength=400,
            text_color="#fca5a5"
        ).pack(pady=5)
        
        ctk.CTkButton(
            error_window,
            text="OK",
            command=error_window.destroy,
            fg_color="#ef4444",
            hover_color="#dc2626",
            corner_radius=8
        ).pack(pady=15)

if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()
