
# README — Uruchomienie projektu

Poniżej znajdziesz gotowy opis pokazujący, jak uruchomić projekt lokalnie i jak zbudować plik `.exe`. Instrukcje zakładają środowisko Windows i Pythona zainstalowanego poza Microsoft Store.  
**Ważne**: pracuj w środowisku wirtualnym (`venv`) — to najlepsza praktyka.

## Wymagania
- Python **3.11.9**  
- System: Windows (instrukcje zawierają polecenia dla PowerShell)
- Zainstalowane pakiety (użyj pliku `requirements.txt`)

## Zawartość `requirements.txt`

Utwórz w repo plik `requirements.txt` zawierający dokładne wersje (przykład):

```
altgraph==0.17.4
astroid==3.3.5
bcrypt==5.0.0
colorama==0.4.6
coverage==7.6.7
dill==0.3.9
greenlet==3.1.1
iniconfig==2.0.0
isort==5.13.2
mccabe==0.7.0
mypy==1.13.0
mypy-extensions==1.0.0
mysql-connector-python==9.1.0
packaging==24.2
pefile==2023.2.7
pip==24.0
platformdirs==4.3.6
pluggy==1.5.0
pyinstaller==6.16.0
pyinstaller-hooks-contrib==2025.9
pylint==3.3.1
pylint-pytest==1.1.8
PyQt6==6.7.1
PyQt6-Qt6==6.7.3
PyQt6_sip==13.8.0
PyQt6-WebEngine==6.7.0
PyQt6-WebEngine-Qt6==6.7.3
PyQt6-WebEngineSubwheel-Qt6==6.7.3
PySide6==6.8.0.2
PySide6_Addons==6.8.0.2
PySide6-DS==4.6
PySide6_Essentials==6.8.0.2
pytest==8.2.0
pytest-cov==6.0.0
pytest-faulthandler==2.0.1
pytest-sugar==1.0.0
pywin32-ctypes==0.2.3
setuptools==65.5.0
shiboken6==6.8.0.2
SQLAlchemy==2.0.36
termcolor==2.5.0
tomlkit==0.13.2
typing_extensions==4.12.2
```

## Krok po kroku — uruchomienie lokalne (development)

1. Sklonuj repo:
```powershell
git clone <URL_REPO>
cd <repo-folder>
```

2. Utwórz środowisko wirtualne i aktywuj:
```powershell
python -m venv .venv
.\.venv\Scriptsctivate
```

3. Zaktualizuj `pip` i zainstaluj zależności:
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

4. Uruchom aplikację:
```powershell
python main.py
```

## Krok po kroku — budowanie pliku `.exe` (Windows)

Uruchom polecenie w katalogu projektu:

```powershell
python -m PyInstaller --windowed --noconfirm --hidden-import=bcrypt --add-data "database:database" --add-data "..\Projekt_inzContent:Projekt_inzContent" main.py
```

Po zakończeniu budowania wynik znajdziesz w `dist/main/`.

## Trwałe rozwiązanie — modyfikacja pliku `.spec`

1. Otwórz `main.spec` po pierwszym buildzie.
2. W `hiddenimports` dodaj `bcrypt`:
```python
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('database', 'database'), ('..\Projekt_inzContent', 'Projekt_inzContent')],
    hiddenimports=['bcrypt'],
    ...
)
```
3. Buduj z użyciem spec:
```powershell
python -m PyInstaller main.spec
```

## Typowe problemy i rozwiązania (FAQ)

- **`ModuleNotFoundError: No module named 'bcrypt'`** — dodaj `--hidden-import=bcrypt` lub wpisz w `main.spec`.
- **`PermissionError` podczas usuwania `dist`** — zamknij uruchomione `main.exe` lub usuń `dist\main` ręcznie:
```powershell
Remove-Item -Recurse -Force .\dist\main
```

## Plik `.gitignore` (sugerowany)
```
__pycache__/
*.py[cod]
*.pyo
*.pyd
.venv/
venv/
dist/
build/
*.spec
Thumbs.db
.DS_Store
```

