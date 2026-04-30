#!/usr/bin/env python3

# Auteur: Yannick SUDRIE
# Date: 29 avril 2026

"""
gps_to_tiles.py - Convertisseur de coordonnées GPS en tuiles Géoportail

Utilisation:
    python gps_to_tiles.py --lon 1.492269 --lat 43.393694 --zoom 18
"""

import math
import argparse

def deg2num(lon_deg, lat_deg, zoom):
    """
    Convertit des coordonnées GPS (degrés) en numéros de tuile (x, y).
    
    Algorithme standardOpenStreetMap / Google Maps / Géoportail.
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile

def num2deg(xtile, ytile, zoom):
    """
    Convertit des numéros de tuile en coordonnées GPS (lon, lat) du coin haut-gauche.
    Utile pour vérifier la zone couverte par une tuile.
    """
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lon_deg, lat_deg

def main():
    parser = argparse.ArgumentParser(
        description="Convertit des coordonnées GPS en numéros de tuile pour le Géoportail."
    )
    parser.add_argument("--lon", type=float, required=True, help="Longitude (ex: 1.492269)")
    parser.add_argument("--lat", type=float, required=True, help="Latitude (ex: 43.393694)")
    parser.add_argument("--zoom", type=int, required=True, choices=range(0, 22), help="Niveau de zoom (0 à 21)")
    
    args = parser.parse_args()
    
    # Calcul des tuiles
    col, row = deg2num(args.lon, args.lat, args.zoom)
    
    # Affichage des résultats
    print("\n" + "="*50)
    print("📐 CONVERSION GPS -> TUILE")
    print("="*50)
    print(f"🌍 Coordonnées entrées : Lon {args.lon}, Lat {args.lat}")
    print(f"🔍 Niveau de zoom (z)   : {args.zoom}")
    print("-" * 50)
    print(f"🧩 Numéro de colonne (x) : {col}")
    print(f"🧩 Numéro de ligne (y)   : {row}")
    print("="*50)
    
    # Optionnel : Afficher un exemple d'URL
    print("\n🔗 Exemple d'URL de tuile (format Géoportail) :")
    base_url = "https://data.geopf.fr/wmts?layer=ORTHOIMAGERY.ORTHOPHOTOS.1950-1965&style=BDORTHOHISTORIQUE&tilematrixset=PM&Service=WMTS&Request=GetTile&Version=1.0.0&Format=image%2Fpng"
    print(f"{base_url}&TileMatrix={args.zoom}&TileCol={col}&TileRow={row}")
    
    # Afficher les coordonnées du coin de la tuile pour vérification
    lon_deg, lat_deg = num2deg(col, row, args.zoom)
    print("\n📌 Coin haut-gauche de cette tuile :")
    print(f"   Lon ≈ {lon_deg:.6f}, Lat ≈ {lat_deg:.6f}")

if __name__ == "__main__":
    main()
