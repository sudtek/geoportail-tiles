@echo off
echo ==========================================
echo 🌍 GEOPORTAIL TILES DOWNLOADER
echo ==========================================
echo Installation des dependances Python
echo.

pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Erreur: pip n'est pas installe
    exit /b 1
)

echo 📋 Environnement Python actuel:
python --version
pip --version
echo.

set /p response="Installer les dependances dans cet environnement? [o/N]: "
if /i not "%response%"=="o" (
    if /i not "%response%"=="oui" (
        echo Installation annulee.
        exit /b 0
    )
)

echo.
echo 📦 Mise a jour de pip...
python -m pip install --upgrade pip

echo.
echo 📦 Installation des dependances...
pip install -r requirements.txt

echo.
echo ✅ Installation terminee !
echo.
echo Pour lancer le script:
echo   python geoportail_tiles.py --help
pause
