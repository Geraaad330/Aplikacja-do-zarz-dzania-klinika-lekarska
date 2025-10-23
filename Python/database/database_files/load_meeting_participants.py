from models.meeting_participants import MeetingParticipants
from controllers.database_controller import DatabaseController
import sqlite3


def load_meeting_participants_data_from_file(file_path):
    """
    Wczytuje dane uczestników spotkań z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi uczestników spotkań.
    :return: Lista krotek z danymi uczestników.
    """
    participants_records = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:  # Pomijamy puste linie
                continue
            try:
                # Rozdzielanie danych według przecinków
                columns = [col.strip() for col in line.split(',')]
                if len(columns) != 5:
                    raise ValueError(f"Niewłaściwa liczba kolumn w wierszu {line_number}.")

                fk_meeting_id = int(columns[1])
                fk_employee_id = int(columns[2])
                participant_role = columns[3]
                attendance = columns[4]

                participants_records.append((fk_meeting_id, fk_employee_id, participant_role, attendance))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return participants_records


def clear_meeting_participants(controller):
    """
    Usuwa wszystkich uczestników spotkań z tabeli `meeting_participants` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        controller.connection.execute("DELETE FROM meeting_participants")
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'meeting_participants'")
        controller.connection.commit()
        print("Wszyscy uczestnicy spotkań zostali usunięci z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")


def add_meeting_participants_to_database(data, controller):
    """
    Dodaje listę uczestników spotkań do bazy danych za pomocą klasy MeetingParticipants.

    :param data: Lista krotek z danymi uczestników spotkań.
    :param controller: Obiekt kontrolera bazy danych.
    """
    participants_model = MeetingParticipants(controller)
    participants_model.create_table()  # Tworzy tabelę `meeting_participants`, jeśli nie istnieje

    for record in data:
        try:
            participants_model.add_participant(*record)
            print(f"Dodano uczestnika spotkania: {record[1]} ({record[2]}).")
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Uczestnik {record[1]} nie został dodany.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Uczestnik {record[1]} nie został dodany.")


if __name__ == "__main__":
    # Ścieżka do pliku z danymi uczestników spotkań
    participants_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\meeting_participants_list.txt"

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich uczestników spotkań
    clear_meeting_participants(db_controller)

    # Wczytanie danych z pliku
    participants_list = load_meeting_participants_data_from_file(participants_file)

    # Dodanie uczestników spotkań do bazy danych
    add_meeting_participants_to_database(participants_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
