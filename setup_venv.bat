@echo off
REM setup_venv.bat - Installation complete avec venv pour Windows

echo ==========================================
echo 🌍 GÉOPORTAIL TILES DOWNLOADER
echo ==========================================
echo Creation de l'environnement virtuel
echo.

set VENV_NAME=geoportail_env
set VENV_DIR=%USERPROFILE%\.venvs\%VENV_NAME%

REM Demander où créer le venv
set /p custom_path="Chemin pour l'environnement virtuel [./%VENV_NAME%]: "
if "%custom_path%"=="" (
    set VENV_DIR=.\%VENV_NAME%
) else (
    set VENV_DIR=%custom_path%
)

REM Créer le venv
echo 📁 Creation de l'environnement virtuel dans: %VENV_DIR%
python -m venv "%VENV_DIR%"

REM Activer le venv
echo 🔄 Activation de l'environnement virtuel...
call "%VENV_DIR%\Scripts\activate.bat"

REM Mettre à jour pip
echo 📦 Mise a jour de pip...
python -m pip install --upgrade pip

REM Installer les dépendances
echo 📦 Installation des dependances...
pip install -r requirements.txt

REM Vérifier l'installation
echo ✅ Verification des installations...
python -c "import requests; print('   ✅ requests', requests.__version__)"
python -c "from PIL import Image; print('   ✅ Pillow', Image.__version__)"

echo.
echo ==========================================
echo ✅ Environnement virtuel pret !
echo ==========================================
echo.
echo Pour utiliser l'environnement:
echo   %VENV_DIR%\Scripts\activate
echo   python DL_geoportail_Tuiles_FINAL.py --help
echo.
echo Pour quitter l'environnement:
echo   deactivate
echo.
pause
