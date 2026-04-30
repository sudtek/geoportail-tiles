#!/bin/bash
# setup_venv.sh - Installation complète avec environnement virtuel

set -e

echo "=========================================="
echo "🌍 GÉOPORTAIL TILES DOWNLOADER"
echo "=========================================="
echo "Création de l'environnement virtuel"
echo ""

VENV_NAME="geoportail_env"

read -p "Chemin pour l'environnement virtuel [./$VENV_NAME]: " custom_path
if [ -z "$custom_path" ]; then
    VENV_DIR="./$VENV_NAME"
else
    VENV_DIR="$custom_path"
fi

echo "📁 Création de l'environnement virtuel dans: $VENV_DIR"
python3 -m venv "$VENV_DIR"

echo "🔄 Activation de l'environnement virtuel..."
source "$VENV_DIR/bin/activate"

echo "📦 Mise à jour de pip..."
pip install --upgrade pip

echo "📦 Installation des dépendances..."
pip install -r requirements.txt

echo ""
echo "✅ Environnement virtuel prêt !"
echo ""
echo "Pour utiliser l'environnement:"
echo "  source $VENV_DIR/bin/activate"
echo "  python geoportail_tiles.py --help"
echo ""
echo "Pour quitter: deactivate"
