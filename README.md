# Funkcjonalność aplikacji

## Widok główny

Po zalogowaniu użytkownik widzi ekran główny z najważniejszymi informacjami:

- aktualna data i dzień tygodnia  
- liczba dzisiejszych wizyt i wszystkich umówionych wizyt (dla personelu medycznego)  
- dane personalne zalogowanego użytkownika, jego rolę i specjalności  

Dostępne są opcje:
- wybór motywu (jasny/ciemny)  
- tryb pełnoekranowy  

---

## Moduł Pacjenci

Zarządza danymi pacjentów, diagnozami i receptami.

- Lista pacjentów zawiera: imię, nazwisko, PESEL, telefon, email, adres, datę urodzenia i status  
- Lista diagnoz i recept zawiera powiązane informacje o pacjentach  
- Możliwość dodawania, aktualizacji i usuwania pacjentów, diagnoz oraz recept  
- Dostęp zależny od roli użytkownika (personel medyczny ma dostęp tylko do swoich pacjentów)  

---

## Moduł Pracownicy

Zarządza danymi pracowników, ich usługami i specjalnościami.

- Lista pracowników z podstawowymi danymi kontaktowymi i statusem aktywności  
- Lista usług i specjalności przypisanych do pracowników  
- Tabele przypisania usług i specjalności ułatwiają organizację pracy  
- Operacje dodawania, aktualizacji i usuwania dostępne dla ról: administrator, recepcjonista, informatyk i kierownik  

---

## Moduł Pokoje i Rezerwacje

Zarządza pokojami i rezerwacjami.

- Lista pokoi z numerem, piętrem i typem  
- Lista rezerwacji z datą, godziną, numerem pokoju i typem rezerwacji  
- Możliwość dodawania, aktualizacji i usuwania pokoi, typów pokoi oraz rezerwacji  
- Dostęp dla wszystkich ról poza rolą gościa  

---

## Moduł Harmonogram

Zarządza wizytami i spotkaniami wewnętrznymi.

- Lista wizyt zawiera dane pacjenta, pracownika, usługę, pokój, datę, godzinę, notatki i status wizyty  
- Lista typów spotkań i spotkań wewnętrznych  
- Możliwość dodawania, aktualizacji i usuwania spotkań oraz uczestników  
- Wszystkie operacje dostępne dla ról z wyjątkiem roli gościa  

---

## Moduł Ustawienia administracyjne

Najbardziej chroniony moduł, dostępny tylko dla Administratora i Informatyka.

- Zarządzanie użytkownikami, rolami i przypisaniami pacjentów do personelu  
- Pełny dostęp do dodawania, aktualizacji i usuwania użytkowników oraz przypisań  
- Kluczowy dla systemu autoryzacji i organizacji opieki nad pacjentem  

---

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
git clone https://github.com/Geraaad330/Aplikacja-do-zarzadzania-klinika-lekarska.git
cd Aplikacja-do-zarzadzania-klinika-lekarska
```

2. Utwórz środowisko wirtualne i aktywuj:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate
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
