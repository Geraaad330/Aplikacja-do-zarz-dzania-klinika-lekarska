from models.meeting_types import MeetingTypes
from controllers.database_controller import DatabaseController
import sqlite3


def load_meeting_types_from_file(file_path):
    """
    Wczytuje dane typów spotkań z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi typów spotkań.
    :return: Lista krotek z danymi typów spotkań.
    """
    meeting_type_records = []
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
                
                meeting_type_id = int(columns[0])  # ID typu spotkania
                meeting_type_name = columns[1]  # Nazwa typu spotkania

                meeting_type_records.append((meeting_type_id, meeting_type_name))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return meeting_type_records


def clear_meeting_types(controller):
    """
    Usuwa wszystkie typy spotkań z tabeli `meeting_types` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        # Usuwanie wszystkich rekordów z tabeli
        controller.connection.execute("DELETE FROM meeting_types")
        
        # Resetowanie licznika autoincrement
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'meeting_types'")
        
        controller.connection.commit()
        print("Wszystkie typy spotkań zostały usunięte z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")


def add_meeting_types_to_database(data, controller):
    """
    Dodaje listę typów spotkań do bazy danych za pomocą klasy MeetingTypes.

    :param data: Lista krotek z danymi typów spotkań.
    :param controller: Obiekt kontrolera bazy danych.
    """
    meeting_types_model = MeetingTypes(controller)
    meeting_types_model.create_table()  # Tworzy tabelę `meeting_types`, jeśli nie istnieje

    for record in data:
        try:
            # Wstawianie danych typu spotkania do bazy
            meeting_types_model.create_new_record(record[1])
            print(f"Dodano typ spotkania: {record[1]}.")
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Typ spotkania {record[1]} nie został dodany.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Typ spotkania {record[1]} nie został dodany.")


if __name__ == "__main__":
    # Ścieżka do pliku z danymi typów spotkań
    meeting_types_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\meeting_types_list.txt"  # Zmień ścieżkę na odpowiednią

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich typów spotkań
    clear_meeting_types(db_controller)

    # Wczytanie danych z pliku
    meeting_types_list = load_meeting_types_from_file(meeting_types_file)

    # Dodanie typów spotkań do bazy danych
    add_meeting_types_to_database(meeting_types_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
