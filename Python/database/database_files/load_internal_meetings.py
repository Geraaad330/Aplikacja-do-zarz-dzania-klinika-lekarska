from models.internal_meetings import InternalMeetings
from controllers.database_controller import DatabaseController
import sqlite3


def load_internal_meetings_data_from_file(file_path):
    """
    Wczytuje dane spotkań wewnętrznych z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi spotkań.
    :return: Lista krotek z danymi spotkań.
    """
    meeting_records = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:  # Pomijamy puste linie
                continue
            try:
                # Rozdzielanie danych według przecinków
                columns = [col.strip() for col in line.split(',')]
                if len(columns) != 6:
                    raise ValueError(f"Niewłaściwa liczba kolumn w wierszu {line_number}.")

                # Odczytujemy dane
                fk_meeting_type_id = int(columns[1])
                fk_reservation_id = int(columns[2])
                meeting_date = columns[3]
                notes = columns[4]
                internal_meeting_status = columns[5]

                meeting_records.append((fk_meeting_type_id, fk_reservation_id, meeting_date, notes, internal_meeting_status))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return meeting_records


def clear_internal_meetings(controller):
    """
    Usuwa wszystkie spotkania wewnętrzne z tabeli `internal_meetings` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        # Usuwanie wszystkich rekordów z tabeli
        controller.connection.execute("DELETE FROM internal_meetings")
        
        # Resetowanie licznika autoincrement
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'internal_meetings'")
        
        controller.connection.commit()
        print("Wszystkie spotkania wewnętrzne zostały usunięte z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")


def add_internal_meetings_to_database(data, controller):
    """
    Dodaje listę spotkań wewnętrznych do bazy danych za pomocą klasy InternalMeetings.

    :param data: Lista krotek z danymi spotkań wewnętrznych.
    :param controller: Obiekt kontrolera bazy danych.
    """
    meetings_model = InternalMeetings(controller)
    meetings_model.create_table()  # Tworzy tabelę `internal_meetings`, jeśli nie istnieje

    for record in data:
        try:
            # Wstawianie danych spotkania do bazy
            meetings_model.add_meeting(*record)
            print(f"Dodano spotkanie: Typ {record[0]},  {record[1]},  {record[2]}.")
        except ValueError as e:
            print(f"Błąd walidacji: {e} {record[0]} {record[1]} nie zostało dodane.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} nie zostało dodane.")


if __name__ == "__main__":
    # Ścieżka do pliku z danymi spotkań
    meetings_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\internal_meetings_list.txt"

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich spotkań wewnętrznych
    clear_internal_meetings(db_controller)

    # Wczytanie danych z pliku
    meetings_list = load_internal_meetings_data_from_file(meetings_file)

    # Dodanie spotkań do bazy danych
    add_internal_meetings_to_database(meetings_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
