from models.specialties import Specialties
from controllers.database_controller import DatabaseController
import sqlite3

def load_specialty_data_from_file(file_path):
    """
    Wczytuje dane specjalizacji z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi specjalizacji.
    :return: Lista krotek z danymi specjalizacji.
    """
    specialty_records = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:  # Pomijamy puste linie
                continue
            try:
                # Rozdzielanie danych według przecinków
                columns = [col.strip() for col in line.split(',')]
                if len(columns) != 2:
                    raise ValueError(f"Niewłaściwa liczba kolumn w wierszu {line_number}.")

                specialty_id = int(columns[0])  # ID specjalizacji
                name = columns[1]  # Nazwa specjalizacji

                specialty_records.append((specialty_id, name))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return specialty_records

def clear_specialties(controller):
    """
    Usuwa wszystkie specjalizacje z tabeli `specialties` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        controller.connection.execute("DELETE FROM specialties")
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'specialties'")
        controller.connection.commit()
        print("Wszystkie specjalizacje zostały usunięte z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")

def add_specialties_to_database(data, controller):
    """
    Dodaje listę specjalizacji do bazy danych za pomocą klasy Specialties.

    :param data: Lista krotek z danymi specjalizacji (tylko nazwy specjalizacji).
    :param controller: Obiekt kontrolera bazy danych.
    """
    specialty_model = Specialties(controller)
    specialty_model.create_table()  # Tworzy tabelę `specialties`, jeśli nie istnieje

    for record in data:
        try:
            # Przekazujemy tylko nazwę specjalności (drugi element krotki)
            specialty_model.create_new_record(record[1])
            print(f"Dodano specjalizację: {record[1]}.")
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Specjalizacja {record[1]} nie została dodana.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Specjalizacja {record[1]} nie została dodana.")


if __name__ == "__main__":
    specialties_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\specialties_list.txt"  # Zmień ścieżkę na właściwą

    db_controller = DatabaseController()
    db_controller.connect_to_database()

    clear_specialties(db_controller)

    specialty_list = load_specialty_data_from_file(specialties_file)

    add_specialties_to_database(specialty_list, db_controller)

    db_controller.connection.close()
