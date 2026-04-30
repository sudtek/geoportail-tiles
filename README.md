    # 🌍 Géoportail Tiles Downloader

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
Téléchargeur et assembleur de tuiles aériennes historiques (1950-1965) depuis le Géoportail français.

## ✨ Fonctionnalités

- 📥 Téléchargement automatique de grilles de tuiles (256x256 pixels)

- 🎯 **Centrage automatique** sur des coordonnées GPS

- 🖼️ Assemblage automatique en une seule image grand format

- 🗑️ Option `--purge` pour nettoyer les tuiles individuelles

- 🔍 Mode verbeux pour suivre l'avancement

- 📁 Nommage intelligent des fichiers (coordonnées, zoom, dimensions)
  
  ## 📋 Prérequis

- Python 3.8 ou supérieur

- pip (gestionnaire de paquets)
  
  ## 🚀 Installation rapide
  
  ### Option 1: Installation automatique (recommandée)
  
  ```bash
  # Linux/Mac
  chmod +x setup_venv.sh
  ./setup_venv.sh
  # Windows
  setup_venv.bat
  ```

### Option 2: Installation manuelle

```bash
# Créer un environnement virtuel
python3 -m venv geoportail_env

# Activer l'environnement
source geoportail_env/bin/activate  # Linux/Mac
geoportail_env\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## 🎯 Utilisation

### Mode centré sur coordonnées GPS (recommandé)

```bash
# Télécharger une zone de 7x7 tuiles autour du point GPS
python geoportail_tiles.py \
    --lon 1.492269 \
    --lat 43.393694 \
    --width 7 \
    --height 7 \
    --zoom 18 \
    --verbose

# Version "propre" (supprime les tuiles individuelles)
python geoportail_tiles.py \
    --lon 1.492269 \
    --lat 43.393694 \
    --width 7 \
    --height 7 \
    --zoom 18 \
    --verbose \
    --purge
```

### Utilitaires

```bash
# Convertir des coordonnées GPS en numéros de tuile
python gps_to_tiles.py --lon 1.492269 --lat 43.393694 --zoom 18

# Afficher l'aide complète
python geoportail_tiles.py --help
```

## 📊 Exemples

### Grille 5x5 centrée sur Notre-Dame de Paris

```bash
python geoportail_tiles.py \
    --lon 2.3499 \
    --lat 48.8530 \
    --width 5 \
    --height 5 \
    --zoom 18 \
    --verbose \
    --purge
```

### Zone plus large (15x15) avec zoom inférieur

```bash
python geoportail_tiles.py \
 --lon 1.492269 \
 --lat 43.393694 \
 --width 15 \
 --height 15 \
 --zoom 16 \
 --verbose
```

## 📁 Structure de sortie

```textile
tuiles_geoportail/
├── lon_1.492269_lat_43.393694_col_132158-132164_row_95931-95937_z18_7x7.png # Image assemblée
└── tuiles/ # (optionnel, sans --purge)
 ├── tile_132158_95931.png
 ├── tile_132158_95932.png
 └── ...
```

## 🕵️ Comment ça fonctionne ?

### Découverte des paramètres (méthodologie)

Pour trouver les paramètres `TileCol` et `TileRow`, nous avons utilisé les outils de développement de Chromium/Chrome :

1. **Ouvrir les outils développeur** (`F12`)

2. **Aller dans l'onglet "Réseau" (Network)**

3. **Naviguer sur [Remonter le temps](https://remonterletemps.ign.fr/)**

4. **Filtrer les requêtes par "png" ou "GetTile"**

5. **Identifier les appels au service WMTS** :
   
   ```context
   https://data.geopf.fr/wmts?layer=...&TileMatrix=18&TileCol=132158&TileRow=95931
   ```

6. **Extraire les paramètres** :
   
   - `TileMatrix` = niveau de zoom
   
   - `TileCol` = colonne X
   
   - `TileRow` = ligne Y

### Conversion GPS → Tuiles

Le script `gps_to_tiles.py` utilise la formule mathématique standard (Web Mercator) utilisée par toutes les plateformes de cartographie (Google Maps, OpenStreetMap, IGN) pour convertir des coordonnées GPS en numéros de tuile.

## 📦 Dépendances

- `requests` : Téléchargement HTTPS

- `Pillow` : Assemblage des images PNG

## 📝 Notes

- Respectez les délais entre les requêtes (100ms par défaut)

- Les dimensions impaires (7x7, 5x5, etc.) offrent un centrage parfait

- Les fichiers déjà téléchargés ne sont pas retéléchargés

## 🐛 Dépannage

### Erreur "No module named 'requests'"

```bash
pip install -r requirements.txt
```

### La tuile centrale n'est pas centrée

Utilisez des dimensions **impaires** (7x7, 9x9, etc.) pour un centrage parfait.

### Téléchargements qui échouent

- Vérifiez votre connexion internet

- Réexécutez le script (reprise automatique)

- Augmentez le délai (`DELAY_BETWEEN_REQUESTS` dans le script)

## 📜 Licence

MIT License - Voir fichier [LICENSE](https://license/)

## 🙏 Remerciements

- [IGN - Géoportail](https://www.geoportail.gouv.fr/) pour la mise à disposition des données

- [Remonter le temps](https://remonterletemps.ign.fr/) pour l'interface de visualisation

## 👤 Auteur

Yannick SUDRIE - Avril 2026

## 🔗 Liens utiles

- [Remonter le temps IGN](https://remonterletemps.ign.fr/)

- [Documentation WMTS Géoportail](https://geoservices.ign.fr/documentation/services/api-et-endpoints)
