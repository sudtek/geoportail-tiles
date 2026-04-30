

# 🔍 Méthodologie : Comment trouver les paramètres des tuiles

Ce document explique la méthode utilisée pour découvrir les paramètres `TileCol` et `TileRow` nécessaires au téléchargement des tuiles.

## Contexte

Le site [Remonter le temps](https://remonterletemps.ign.fr/) de l'IGN affiche des orthophotos historiques sous forme de tuiles (tiles). Pour automatiser le téléchargement, nous avons besoin de connaître les paramètres exacts utilisés par le site.

## Méthode pas à pas

### 1. Ouvrir les outils de développement

Dans **Chromium/Chrome** (identique sur Brave, Edge, Opera) :

- Appuyer sur `F12` (ou `Ctrl+Shift+I` sous Windows, `Cmd+Option+I` sous Mac)
- Aller dans l'onglet **Réseau** (Network)

### 2. Naviguer sur le site

- Aller sur [Remonter le temps](https://remonterletemps.ign.fr/)
- Centrer la carte sur la zone souhaitée
- Choisir le niveau de zoom approprié

### 3. Capturer les requêtes réseau

- **Effacer** l'historique réseau (bouton 🚫)
- **Recharger** la page (`F5`)
- Observer les requêtes qui apparaissent

### 4. Filtrer les tuiles

![28_avril_2026_remonterletemps.ign.fr.jpg](https://github.com/sudtek/geoportail-tiles/blob/d425bacd626f11c5c980cfb63842753bc2a5493a/archive/28_avril_2026_remonterletemps.ign.fr.jpg)

### 5. Identifier les requêtes WMTS

Chercher des URLs qui ressemblent à :

[https://data.geopf.fr/wmts?layer=ORTHOIMAGERY.ORTHOPHOTOS.1950-1965&style=BDORTHOHISTORIQUE&tilematrixset=PM&Service=WMTS&Request=GetTile&Version=1.0.0&Format=image%2Fpng&TileMatrix=18&TileCol=132158&TileRow=95931](https://data.geopf.fr/wmts?layer=ORTHOIMAGERY.ORTHOPHOTOS.1950-1965&style=BDORTHOHISTORIQUE&tilematrixset=PM&Service=WMTS&Request=GetTile&Version=1.0.0&Format=image%252Fpng&TileMatrix=18&TileCol=132158&TileRow=95931)

### 6. Extraire les paramètres

Dans l'URL, repérer :

- `TileMatrix` = Niveau de zoom (ex: 18)
- `TileCol` = Colonne X (ex: 132158)
- `TileRow` = Ligne Y (ex: 95931)

### 7. Convertir en coordonnées GPS (optionnel)

Si besoin de connaître les coordonnées GPS correspondant à une tuile, utiliser la formule mathématique (voir `gps_to_tiles.py`).

## Capture d'écran illustrative

```textile
Outils développeur - Onglet Réseau
┌─────────────────────────────────────────────────────────────┐
│ 🔍 Filtrer: png ⚡ │
├─────────────────────────────────────────────────────────────┤
│ 📄 GetTile?TileMatrix=18&TileCol=132158&TileRow=95931 │
│ └── Statut: 200 Type: image/png Taille: 34KB │
│ 📄 GetTile?TileMatrix=18&TileCol=132158&TileRow=95932 │
│ └── Statut: 200 Type: image/png Taille: 35KB │
│ 📄 GetTile?TileMatrix=18&TileCol=132159&TileRow=95931 │
│ └── Statut: 200 Type: image/png Taille: 33KB │
└─────────────────────────────────────────────────────────────┘
```

## Outil alternatif

Pour éviter de refaire cette manipulation à chaque fois, nous avons créé `gps_to_tiles.py` qui convertit directement des coordonnées GPS en numéros de tuile :

```bash
python gps_to_tiles.py --lon 1.492269 --lat 43.393694 --zoom 18
```



### Acquisition des coordonnées GPS

Les coordonnées GPS sont directement lisibles dans l'URL du site :

```textile
https://remonterletemps.ign.fr/comparer/?lon=1.492269&lat=43.393694&z=18.2
                                                ↑              ↑
                                             Longitude      Latitude
```

## Notes importantes

- Le niveau de zoom (`z` dans l'URL) est un nombre réel (ex: 18.2)

- Le `TileMatrix` doit être un entier (ex: 18)

- La conversion de GPS à tuile utilise un arrondi standard

- Les tuiles font toujours 256x256 pixels

## Évolution de la méthode

**Version POC (v0.1)** : Capture manuelle des URL via les outils développeur  
**Version finale (v2.0)** : Conversion automatique GPS → Tuile via calcul mathématique

Cette automatisation a permis de créer `geoportail_tiles.py` qui accepte directement des coordonnées GPS, rendant l'outil accessible à tous, sans connaissance technique particulière.
