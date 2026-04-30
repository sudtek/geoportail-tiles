#!/usr/bin/env python3

"""
geoportail_tiles.py

Téléchargeur et assembleur (merge) de tuiles aériennes historiques depuis le Géoportail français.
Version: 2.0
Auteur: Yannick SUDRIE
Date: 29 avril 2026

Description:
    Télécharge des tuiles 256x256 pixels depuis le service WMTS du Géoportail
    pour les orthophotos historiques (1950-1965) et les assemble en une seule image.
"""

import requests
import os
import sys
import argparse
import time
import shutil
from pathlib import Path
from PIL import Image

# Configuration par défaut
DEFAULT_ZOOM = 18
DEFAULT_OUTPUT_DIR = "tuiles_geoportail"
DELAY_BETWEEN_REQUESTS = 0.1
USER_AGENT = "GeoportailTileDownloader/2.0"

# URL de base du service WMTS
BASE_URL = "https://data.geopf.fr/wmts"
LAYER = "ORTHOIMAGERY.ORTHOPHOTOS.1950-1965"
STYLE = "BDORTHOHISTORIQUE"
FORMAT = "image/png"

# Taille des tuiles en pixels
TILE_WIDTH = 256
TILE_HEIGHT = 256


class GeoportailTileDownloader:
    """Téléchargeur et assembleur de tuiles Géoportail"""
    
    def __init__(self, start_col, start_row, nb_cols, nb_rows, zoom, 
                 lon=None, lat=None, output_dir="tuiles_geoportail", 
                 assemble=True, purge=False, verbose=False):
        """
        Initialise le téléchargeur
        
        Args:
            start_col: Colonne de départ
            start_row: Ligne de départ
            nb_cols: Nombre de colonnes
            nb_rows: Nombre de lignes
            zoom: Niveau de zoom
            lon: Longitude (optionnel, pour le nommage)
            lat: Latitude (optionnel, pour le nommage)
            output_dir: Répertoire de sortie
            assemble: Assembler les tuiles après téléchargement
            purge: Supprimer les tuiles individuelles après assemblage
            verbose: Mode verbeux
        """
        self.start_col = start_col
        self.start_row = start_row
        self.nb_cols = nb_cols
        self.nb_rows = nb_rows
        self.zoom = zoom
        self.lon = lon
        self.lat = lat
        self.output_dir = Path(output_dir)
        self.assemble = assemble
        self.purge = purge
        self.verbose = verbose
        self.downloaded = 0
        self.failed = 0
        self.skipped = 0
        
        # Créer le répertoire de sortie
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sous-répertoire pour les tuiles individuelles (si purge=False)
        if not self.purge:
            self.tiles_dir = self.output_dir / "tuiles"
            self.tiles_dir.mkdir(exist_ok=True)
        else:
            self.tiles_dir = self.output_dir
    
    def log(self, message, level="INFO"):
        """Affiche un message si mode verbeux actif"""
        if self.verbose or level in ["ERROR", "WARNING"]:
            print(f"[{level}] {message}")
    
    def build_url(self, col, row):
        """Construit l'URL pour une tuile spécifique"""
        url = f"{BASE_URL}?layer={LAYER}&style={STYLE}&tilematrixset=PM&Service=WMTS&Request=GetTile&Version=1.0.0&Format={FORMAT}&TileMatrix={self.zoom}&TileCol={col}&TileRow={row}"
        return url
    
    def get_tile_filename(self, col, row):
        """Génère le nom de fichier pour une tuile"""
        return self.tiles_dir / f"tile_{col}_{row}.png"
    
    def get_merged_filename(self):
        """Génère le nom du fichier assemblé"""
        # Construire un nom explicite
        parts = []
        
        # Ajouter les coordonnées GPS si disponibles
        if self.lon is not None and self.lat is not None:
            parts.append(f"lon_{self.lon:.6f}")
            parts.append(f"lat_{self.lat:.6f}")
        
        # Ajouter les coordonnées tuile
        parts.append(f"col_{self.start_col}-{self.start_col + self.nb_cols - 1}")
        parts.append(f"row_{self.start_row}-{self.start_row + self.nb_rows - 1}")
        
        # Ajouter le zoom
        parts.append(f"z{self.zoom}")
        
        # Ajouter la taille de la grille
        parts.append(f"{self.nb_cols}x{self.nb_rows}")
        
        # Nom final
        filename = "_".join(parts) + ".png"
        
        return self.output_dir / filename
    
    def download_tile(self, col, row):
        """
        Télécharge une tuile
        
        Returns:
            bool: True si succès, False sinon
        """
        filename = self.get_tile_filename(col, row)
        
        # Vérifier si le fichier existe déjà
        if filename.exists():
            self.log(f"Fichier déjà existant: {filename.name}", "SKIP")
            self.skipped += 1
            return True
        
        url = self.build_url(col, row)
        self.log(f"Téléchargement: {filename.name} (col={col}, row={row})")
        
        try:
            headers = {'User-Agent': USER_AGENT}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Vérification du type de contenu
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type:
                self.log(f"Contenu inattendu pour {filename.name}: {content_type}", "WARNING")
            
            # Sauvegarde du fichier
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            self.log(f"Téléchargé: {filename.name} ({len(response.content)} bytes)", "SUCCESS")
            self.downloaded += 1
            return True
            
        except requests.exceptions.Timeout:
            self.log(f"Timeout pour {filename.name}", "ERROR")
            self.failed += 1
            return False
        except requests.exceptions.RequestException as e:
            self.log(f"Erreur réseau pour {filename.name}: {e}", "ERROR")
            self.failed += 1
            return False
        except Exception as e:
            self.log(f"Erreur inattendue pour {filename.name}: {e}", "ERROR")
            self.failed += 1
            return False
    
    def assemble_tiles(self):
        """Assemble toutes les tuiles en une seule image"""
        self.log("Assemblage des tuiles en une seule image...")
        
        # Calculer la taille de l'image finale
        width = self.nb_cols * TILE_WIDTH
        height = self.nb_rows * TILE_HEIGHT
        
        # Créer l'image de sortie
        output_image = Image.new("RGB", (width, height))
        
        # Assembler les tuiles
        missing_tiles = []
        for col in range(self.nb_cols):
            for row in range(self.nb_rows):
                # Calculer les coordonnées absolues de la tuile
                abs_col = self.start_col + col
                abs_row = self.start_row + row
                
                # Chemin de la tuile
                tile_path = self.get_tile_filename(abs_col, abs_row)
                
                if not tile_path.exists():
                    missing_tiles.append((abs_col, abs_row))
                    self.log(f"Tuile manquante: {tile_path.name}", "WARNING")
                    continue
                
                try:
                    tile = Image.open(tile_path)
                    # Position dans l'image finale
                    x = col * TILE_WIDTH
                    y = row * TILE_HEIGHT
                    
                    # Gérer la transparence si nécessaire
                    if tile.mode == 'RGBA':
                        output_image.paste(tile, (x, y), tile)
                    else:
                        output_image.paste(tile, (x, y))
                    
                    self.log(f"Assemblée: {tile_path.name} à position ({x}, {y})")
                    
                except Exception as e:
                    self.log(f"Erreur lors de l'assemblage de {tile_path.name}: {e}", "ERROR")
                    missing_tiles.append((abs_col, abs_row))
        
        # Sauvegarder l'image finale
        if missing_tiles:
            print(f"\n⚠️  ATTENTION: {len(missing_tiles)} tuiles manquantes!")
            print("   L'image finale aura des zones vides.")
        
        merged_filename = self.get_merged_filename()
        output_image.save(merged_filename)
        print(f"\n✅ Image assemblée sauvegardée: {merged_filename}")
        print(f"   Dimensions: {width} x {height} pixels")
        
        return len(missing_tiles) == 0
    
    def purge_tiles(self):
        """Supprime les tuiles individuelles après assemblage"""
        if not self.purge:
            return
        
        self.log("Suppression des tuiles individuelles...")
        deleted_count = 0
        
        for col in range(self.start_col, self.start_col + self.nb_cols):
            for row in range(self.start_row, self.start_row + self.nb_rows):
                tile_path = self.get_tile_filename(col, row)
                if tile_path.exists():
                    tile_path.unlink()
                    deleted_count += 1
        
        self.log(f"Supprimées: {deleted_count} tuiles individuelles")
        
        # Supprimer le répertoire des tuiles s'il est vide
        try:
            if self.tiles_dir != self.output_dir:
                self.tiles_dir.rmdir()
                self.log(f"Répertoire supprimé: {self.tiles_dir}")
        except OSError:
            pass  # Répertoire non vide ou autre erreur
    
    def download_all(self):
        """Télécharge toutes les tuiles de la grille"""
        total_tiles = self.nb_cols * self.nb_rows
        self.log(f"Démarrage du téléchargement de {total_tiles} tuiles")
        self.log(f"Grille: {self.nb_cols} x {self.nb_rows} (zoom {self.zoom})")
        self.log(f"Colonnes: {self.start_col} à {self.start_col + self.nb_cols - 1}")
        self.log(f"Lignes: {self.start_row} à {self.start_row + self.nb_rows - 1}")
        self.log(f"Répertoire de sortie: {self.output_dir}/")
        
        if self.purge:
            self.log("Mode PURGE activé: les tuiles seront supprimées après assemblage")
        
        start_time = time.time()
        
        # Téléchargement des tuiles
        for col in range(self.start_col, self.start_col + self.nb_cols):
            for row in range(self.start_row, self.start_row + self.nb_rows):
                self.download_tile(col, row)
                
                # Petit délai pour ne pas surcharger le serveur
                if (col != self.start_col + self.nb_cols - 1) or (row != self.start_row + self.nb_rows - 1):
                    time.sleep(DELAY_BETWEEN_REQUESTS)
        
        elapsed_time = time.time() - start_time
        
        # Affichage du résumé du téléchargement
        print("\n" + "="*50)
        print("RÉSUMÉ DU TÉLÉCHARGEMENT")
        print("="*50)
        print(f"Total tuiles: {total_tiles}")
        print(f"✅ Téléchargées: {self.downloaded}")
        print(f"⚠️  Déjà existantes: {self.skipped}")
        print(f"❌ Échecs: {self.failed}")
        print(f"⏱️  Temps téléchargement: {elapsed_time:.2f} secondes")
        
        # Assemblage si demandé
        if self.assemble and self.downloaded + self.skipped > 0:
            print("\n" + "="*50)
            print("ASSEMBLAGE DES TUILES")
            print("="*50)
            assemble_success = self.assemble_tiles()
            
            # Purge si demandée et assemblage réussi
            if self.purge and assemble_success:
                self.purge_tiles()
        elif self.assemble:
            print("\n⚠️  Aucune tuile téléchargée, assemblage ignoré.")
        
        # Résumé final
        print("\n" + "="*50)
        print("RÉSUMÉ FINAL")
        print("="*50)
        if self.assemble:
            output_file = self.get_merged_filename()
            print(f"📁 Image finale: {output_file}")
            if self.purge:
                print("🗑️  Mode purge: les tuiles individuelles ont été supprimées")
            else:
                print(f"📂 Tuiles individuelles: {self.tiles_dir}/")
        else:
            print(f"📂 Tuiles individuelles: {self.tiles_dir}/")
        
        if self.failed > 0:
            print("\n⚠️  Certaines tuiles n'ont pas été téléchargées.")
            print("   Réexécutez le script pour réessayer.")
        
        return self.failed == 0


def check_dependencies():
    """Vérifie que les dépendances nécessaires sont installées"""
    try:
        import requests
        from PIL import Image
        return True
    except ImportError as e:
        print("\n❌ ERREUR: Bibliothèque manquante!")
        print(f"   {e}")
        print("\nPour installer les dépendances, exécutez:")
        print("  pip install requests Pillow")
        return False


def calculate_centered_grid(center_col, center_row, width, height):
    """
    Calcule les coordonnées de grille centrées sur une tuile spécifique
    
    Args:
        center_col: Colonne de la tuile centrale
        center_row: Ligne de la tuile centrale
        width: Largeur totale de la grille (nombre de colonnes)
        height: Hauteur totale de la grille (nombre de lignes)
    
    Returns:
        (start_col, start_row): Coordonnées de départ de la grille
    """
    # Calculer le décalage pour centrer la tuile
    offset_cols = (width - 1) // 2
    offset_rows = (height - 1) // 2
    
    # Coordonnées de départ
    start_col = center_col - offset_cols
    start_row = center_row - offset_rows
    
    return start_col, start_row

def get_center_tile_from_gps(lon, lat, zoom):
    """
    Calcule la tuile centrale à partir des coordonnées GPS
    
    Args:
        lon: Longitude
        lat: Latitude
        zoom: Niveau de zoom
    
    Returns:
        (col, row): Coordonnées de la tuile centrale
    """
    # Conversion GPS -> tuile (même formule que dans gps_to_tiles.py)
    import math
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    col = int((lon + 180.0) / 360.0 * n)
    row = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return col, row

def main():
    """Fonction principale"""
    
    print("\n" + "="*60)
    print("🌍 GÉOPORTAIL TILES DOWNLOADER & ASSEMBLEUR")
    print("="*60)
    print("ℹ️  Note: Il est recommandé d'exécuter ce script dans un")
    print("   environnement virtuel (venv) pour éviter de polluer")
    print("   votre installation Python système.\n")
    
    if not check_dependencies():
        sys.exit(1)
    
    # Configuration du parseur d'arguments
    parser = argparse.ArgumentParser(
        description="Téléchargeur et assembleur de tuiles aériennes historiques du Géoportail (1950-1965)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLES D'UTILISATION:

  # MODE CENTRAGE GPS (RECOMMANDE)
  # La tuile contenant les coordonnées GPS sera au centre de l'image
  
  %(prog)s --lon 1.492269 --lat 43.393694 --width 7 --height 7 --zoom 18 --verbose
  
  # Avec suppression des tuiles individuelles (propre)
  %(prog)s --lon 1.492269 --lat 43.393694 --width 7 --height 7 --zoom 18 --verbose --purge
  
  # MODE CENTRAGE MANUEL
  # Centrer sur une tuile spécifique
  
  %(prog)s --center-col 132158 --center-row 95931 --width 7 --height 7 --zoom 18 --verbose
  
  # MODE LEGACY (coin haut-gauche)
  # Pour compatibilité avec l'ancienne version
  
  %(prog)s --col-start 132154 --row-start 95928 --width 7 --height 7 --zoom 18
  
  # Sans assemblage (garde les tuiles individuelles)
  %(prog)s --lon 1.492269 --lat 43.393694 --width 7 --height 7 --zoom 18 --no-assemble

NOTE SUR LE CENTRAGE:
  Pour un centrage parfait, utilisez des dimensions impaires (7x7, 5x5, 9x9...).
  Avec des dimensions paires, la tuile centrale sera légèrement décalée.
  
  Flux de travail typique:
  1. python gps_to_tiles.py --lon 1.492269 --lat 43.393694 --zoom 18
  2. %(prog)s --lon 1.492269 --lat 43.393694 --width 7 --height 7 --zoom 18 --verbose --purge
        """
    )
    
    # Arguments pour les différents modes
    parser.add_argument('--lon', type=float, help='Longitude (active le mode centrage GPS)')
    parser.add_argument('--lat', type=float, help='Latitude (active le mode centrage GPS)')
    
    parser.add_argument('--center-col', type=int, help='Colonne centrale (mode centrage manuel)')
    parser.add_argument('--center-row', type=int, help='Ligne centrale (mode centrage manuel)')
    
    parser.add_argument('--col-start', type=int, help='Colonne de départ (mode legacy)')
    parser.add_argument('--row-start', type=int, help='Ligne de départ (mode legacy)')
    
    # Dimensions de la grille
    parser.add_argument('--width', type=int, required=True, 
                       help='Nombre de colonnes (largeur de la grille)')
    parser.add_argument('--height', type=int, required=True, 
                       help='Nombre de lignes (hauteur de la grille)')
    
    # Options générales
    parser.add_argument('--zoom', type=int, default=DEFAULT_ZOOM, choices=range(0, 21),
                       help=f'Niveau de zoom (0-20, défaut: {DEFAULT_ZOOM})')
    parser.add_argument('--output-dir', type=str, default=DEFAULT_OUTPUT_DIR,
                       help=f'Répertoire de sortie (défaut: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--no-assemble', action='store_false', dest='assemble',
                       help='Ne pas assembler les tuiles (les garde individuelles)')
    parser.add_argument('--purge', action='store_true',
                       help='Supprime les tuiles individuelles après assemblage')
    parser.add_argument('--verbose', action='store_true', 
                       help='Mode verbeux (affiche les détails)')
    parser.add_argument('--no-delay', action='store_true',
                       help='Supprime le délai entre les requêtes (non recommandé)')
    
    args = parser.parse_args()
    
    # ============================================================
    # LOGIQUE DE CENTRAGE
    # ============================================================
    
    start_col = None
    start_row = None
    center_tile_col = None
    center_tile_row = None
    
    # Vérifier qu'on a bien un seul mode de centrage
    modes = 0
    if args.lon is not None and args.lat is not None:
        modes += 1
    if args.center_col is not None and args.center_row is not None:
        modes += 1
    if args.col_start is not None and args.row_start is not None:
        modes += 1
    
    if modes == 0:
        print("\n❌ ERREUR: Vous devez spécifier un mode de centrage:")
        print("   Mode GPS       : --lon et --lat")
        print("   Mode manuel    : --center-col et --center-row")
        print("   Mode legacy    : --col-start et --row-start")
        sys.exit(1)
    
    if modes > 1:
        print("\n❌ ERREUR: Spécifiez un seul mode de centrage")
        print("   (GPS, manuel ou legacy, pas plusieurs à la fois)")
        sys.exit(1)
    
    # ============================================================
    # MODE 1: Centrage GPS automatique
    # ============================================================
    
    if args.lon is not None and args.lat is not None:
        print("\n📍 MODE CENTRAGE GPS")
        print(f"   Coordonnées: lon={args.lon}, lat={args.lat}, zoom={args.zoom}")
        
        # Calculer la tuile centrale à partir des coordonnées GPS
        import math
        lat_rad = math.radians(args.lat)
        n = 2.0 ** args.zoom
        center_tile_col = int((args.lon + 180.0) / 360.0 * n)
        center_tile_row = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        
        print(f"   Tuile centrale calculée: col={center_tile_col}, row={center_tile_row}")
        
        # Calculer la grille centrée
        offset_cols = (args.width - 1) // 2
        offset_rows = (args.height - 1) // 2
        
        start_col = center_tile_col - offset_cols
        start_row = center_tile_row - offset_rows
        
        print(f"   Grille générée: [{start_col}..{start_col + args.width - 1}] x [{start_row}..{start_row + args.height - 1}]")
        
        # Avertissement pour dimensions paires
        if args.width % 2 == 0 or args.height % 2 == 0:
            print("\n⚠️  ATTENTION: Pour un centrage parfait, utilisez des dimensions impaires!")
            print(f"   Largeur={args.width} (impaire recommandée), Hauteur={args.height} (impaire recommandée)")
            print("   Avec des dimensions paires, la tuile centrale sera légèrement décalée.\n")
            response = input("Continuer quand même? (o/N): ")
            if response.lower() != 'o':
                print("Téléchargement annulé.")
                sys.exit(0)
    
    # ============================================================
    # MODE 2: Centrage manuel
    # ============================================================
    
    elif args.center_col is not None and args.center_row is not None:
        print("\n📍 MODE CENTRAGE MANUEL")
        print(f"   Tuile centrale: col={args.center_col}, row={args.center_row}")
        
        center_tile_col = args.center_col
        center_tile_row = args.center_row
        
        # Calculer la grille centrée
        offset_cols = (args.width - 1) // 2
        offset_rows = (args.height - 1) // 2
        
        start_col = center_tile_col - offset_cols
        start_row = center_tile_row - offset_rows
        
        print(f"   Grille générée: [{start_col}..{start_col + args.width - 1}] x [{start_row}..{start_row + args.height - 1}]")
        
        # Avertissement pour dimensions paires
        if args.width % 2 == 0 or args.height % 2 == 0:
            print("\n⚠️  ATTENTION: Pour un centrage parfait, utilisez des dimensions impaires!")
            print(f"   Largeur={args.width} (impaire recommandée), Hauteur={args.height} (impaire recommandée)\n")
            response = input("Continuer quand même? (o/N): ")
            if response.lower() != 'o':
                print("Téléchargement annulé.")
                sys.exit(0)
    
    # ============================================================
    # MODE 3: Legacy (coin haut-gauche)
    # ============================================================
    
    elif args.col_start is not None and args.row_start is not None:
        print("\n📌 MODE LEGACY (coin haut-gauche)")
        print(f"   Départ: col={args.col_start}, row={args.row_start}")
        print(f"   Grille: {args.width} x {args.height}")
        
        start_col = args.col_start
        start_row = args.row_start
    
    # ============================================================
    # VALIDATIONS FINALES
    # ============================================================
    
    # Vérifier les dimensions
    if args.width <= 0 or args.height <= 0:
        print("\n❌ ERREUR: La largeur et la hauteur doivent être positives")
        sys.exit(1)
    
    # Vérifier la taille de la grille
    if args.width > 100 or args.height > 100:
        print("\n⚠️  ATTENTION: Une grille de plus de 100x100 tuiles est très grande!")
        print(f"   Cela représente {args.width * args.height} tuiles à télécharger.")
        response = input("Voulez-vous continuer? (o/N): ")
        if response.lower() != 'o':
            print("Téléchargement annulé.")
            sys.exit(0)
    
    # Vérifier la cohérence de --purge
    if args.purge and not args.assemble:
        print("\n⚠️  ATTENTION: --purge sans assemblage n'a pas de sens")
        print("   Activation automatique de l'assemblage")
        args.assemble = True
    
    # Gérer le délai
    if args.no_delay:
        global DELAY_BETWEEN_REQUESTS
        DELAY_BETWEEN_REQUESTS = 0
        print("\n⚠️  Mode sans délai activé - Risque de limitation par le serveur!")
    
    print("\n" + "="*60)
    print("🚀 DÉMARRAGE DU TÉLÉCHARGEMENT")
    print("="*60)
    
    # ============================================================
    # CRÉATION ET EXÉCUTION DU TÉLÉCHARGEUR
    # ============================================================
    
    # Créer le téléchargeur
    downloader = GeoportailTileDownloader(
        start_col=start_col,
        start_row=start_row,
        nb_cols=args.width,
        nb_rows=args.height,
        zoom=args.zoom,
        lon=args.lon if args.lon else None,
        lat=args.lat if args.lat else None,
        output_dir=args.output_dir,
        assemble=args.assemble,
        purge=args.purge,
        verbose=args.verbose
    )
    
    # Exécuter avec gestion des interruptions
    try:
        success = downloader.download_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Téléchargement interrompu par l'utilisateur")
        print(f"✅ {downloader.downloaded} tuiles ont été téléchargées avec succès")
        if downloader.assemble and downloader.downloaded > 0:
            print("ℹ️  L'assemblage partiel peut être tenté en relançant le script")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
