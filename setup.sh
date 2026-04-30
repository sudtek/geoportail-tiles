#!/bin/bash
# setup.sh - Installation simple des dépendances

set -e

echo "=========================================="
echo "🌍 GÉOPORTAIL TILES DOWNLOADER"
echo "=========================================="
echo "Installation des dépendances Python"
echo ""

if ! command -v pip &> /dev/null; then
    echo "❌ Erreur: pip n'est pas installé"
    exit 1
fi

echo "📋 Environnement Python actuel:"
echo "   Python: $(which python)"
echo "   Pip: $(which pip)"
echo ""

read -p "Installer les dépendances dans cet environnement? [o/N]: " -r response
if [[ ! "$response" =~ ^[oOoui]$ ]]; then
    echo "Installation annulée."
    exit 0
fi

echo ""
echo "📦 Mise à jour de pip..."
pip install --upgrade pip

echo ""
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

echo ""
echo "✅ Installation terminée !"
echo ""
echo "Pour lancer le script:"
echo "  python geoportail_tiles.py --help"
