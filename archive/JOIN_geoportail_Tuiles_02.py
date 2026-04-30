#!/usr/bin/env python3

# yannick SUDRIE
# 05_mai_2025
# v0.1
#
# But : Assembler en une seule image les tuilles 256x256 téléchargées via le script DL_geoportail_Tuiles_01.py

# Note #1 : A lancer dans un venv pour pas polluer avec les dependances !!
# Note #2 : Penser à installer pip dans le venv "pip install" et le mettre à jour  "python -m pip install --upgrade pip", suivi d'un "pip install pillow" !!
# Note #3 : le script affiche un warning concernant la gestion de la transparence mais qui ne pose pas de pb dans ce cas.

""" 
note du 29 mai 2026 : Ce script a juste vocation éducative pour comprendre la tambouille de départ !
"""

from PIL import Image

# Exemple pour une grille 7x7
tile_width, tile_height = 256, 256
grid_width, grid_height = 7, 7
output = Image.new("RGB", (tile_width * grid_width, tile_height * grid_height))

for col in range(grid_width):
    for row in range(grid_height):
        tile = Image.open(f"tile_{132154 + col}_{95928 + row}.png")
        output.paste(tile, (col * tile_width, row * tile_height))

output.save("assembled_image.png")
