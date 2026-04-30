#!/usr/bin/env python3

# yannick SUDRIE
# 05_mai_2025
# v0.1
#
# But : Télecharger à partir de coordonnées GPS standards des prises de vues aériennes de 1190 à 1960 au format tuiles 256x256.
# voir le site https://remonterletemps.ign.fr/comparer/?lon=1.492269&lat=43.393694&z=18.2&pointer=true&layer1=19&layer2=19&mode=split-h

""" 
note du 29 mai 2026 : J'ai utilisé le mode debug F12 du browser chromium pour trouver les réferences des tuiles correspondantes dasn les urls des images au coordonnées lat,long zoom recherchés c'est bien pour tester et verifier à la mano et comprendre mais c'est fastideux -> il faut automatiser ... J'étais parti dans l'idée d'utiliser chrome en headless approche compliquée et j'ai decouvert qu'il existe une api ... 
Ce script a juste vocation éducative pour comprendre la tambouille de départ !

"""

import requests
import os

base_url = "https://data.geopf.fr/wmts?layer=ORTHOIMAGERY.ORTHOPHOTOS.1950-1965&style=BDORTHOHISTORIQUE&tilematrixset=PM&Service=WMTS&Request=GetTile&Version=1.0.0&Format=image%2Fpng&TileMatrix=20"
col_range = range(132154, 132161)  # Exemple : 7 tuiles
row_range = range(95928, 95935)   # Exemple : 7 tuiles

for col in col_range:
    for row in row_range:
        url = f"{base_url}&TileCol={col}&TileRow={row}"
        response = requests.get(url)
        if response.status_code == 200:
            with open(f"tile_{col}_{row}.png", "wb") as f:
                f.write(response.content)
            print(f"Downloaded tile {col}_{row}")
        else:
            print(f"Failed to download tile {col}_{row}")
