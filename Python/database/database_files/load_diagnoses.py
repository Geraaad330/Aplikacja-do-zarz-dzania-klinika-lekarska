from models.diagnoses import Diagnoses
from controllers.database_controller import DatabaseController
import sqlite3


def load_diagnoses_data_from_file(file_path):
    """
    Wczytuje dane diagnoz z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi diagnoz.
    :return: Lista krotek z danymi diagnoz.
    """
    diagnoses_records = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:  # Pomijamy puste linie
                continue
            try:
                # Rozdzielanie danych według przecinków
                columns = [col.strip() for col in line.split(',')]
                if len(columns) != 4:
                    raise ValueError(f"Niewłaściwa liczba kolumn w wierszu {line_number}.")
                
                # Odczytujemy dane
                fk_appointment_id = int(columns[1])  # ID pacjenta
                description = columns[2]  # Nazwa diagnozy
                icd11_code = columns[3]  # Kod diagnozy

                diagnoses_records.append((fk_appointment_id, description, icd11_code))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return diagnoses_records


def clear_diagnoses(controller):
    """
    Usuwa wszystkie diagnozy z tabeli `diagnoses` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        # Usuwanie wszystkich rekordów z tabeli
        controller.connection.execute("DELETE FROM diagnoses")
        
        # Resetowanie licznika autoincrement
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'diagnoses'")
        
        controller.connection.commit()
        print("Wszystkie diagnozy zostały usunięte z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")


def add_diagnoses_to_database(data, controller):
    """
    Dodaje listę diagnoz do bazy danych za pomocą klasy Diagnoses.

    :param data: Lista krotek z danymi diagnoz.
    :param controller: Obiekt kontrolera bazy danych.
    """
    diagnoses_model = Diagnoses(controller)
    diagnoses_model.create_table()  # Tworzy tabelę `diagnoses`, jeśli nie istnieje

    for record in data:
        try:
            # Wstawianie danych diagnozy do bazy
            diagnoses_model.add_diagnosis(*record)
            print(f"Dodano diagnozę: {record[1]} ({record[2]}).")
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Diagnoza {record[1]} nie została dodana.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Diagnoza {record[1]} nie została dodana.")


if __name__ == "__main__":
    # Ścieżka do pliku z danymi diagnoz
    diagnoses_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\diagnoses_list.txt"

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich diagnoz
    clear_diagnoses(db_controller)

    # Wczytanie danych z pliku
    diagnoses_list = load_diagnoses_data_from_file(diagnoses_file)

    # Dodanie diagnoz do bazy danych
    add_diagnoses_to_database(diagnoses_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
