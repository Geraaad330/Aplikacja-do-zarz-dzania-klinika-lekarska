from models.assigned_patients import AssignedPatients
from controllers.database_controller import DatabaseController
import sqlite3


def load_assigned_patients_from_file(file_path):
    """
    Wczytuje dane przypisanych pacjentów z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi przypisanych pacjentów.
    :return: Lista krotek z danymi przypisanych pacjentów.
    """
    assigned_patients_records = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:  # Pomijamy puste linie
                continue
            try:
                # Rozdzielanie danych według przecinków
                columns = [col.strip() for col in line.split(',')]
                if len(columns) != 3:
                    raise ValueError(f"Niewłaściwa liczba kolumn w wierszu {line_number}.")

                participant_id = int(columns[0])  # ID przypisania
                fk_employee_id = int(columns[1])  # ID pracownika
                fk_patient_id = int(columns[2])  # ID pacjenta

                assigned_patients_records.append((participant_id, fk_employee_id, fk_patient_id))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return assigned_patients_records


def clear_assigned_patients(controller):
    """
    Usuwa wszystkich przypisanych pacjentów z tabeli `assigned_patients` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        controller.connection.execute("DELETE FROM assigned_patients")
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'assigned_patients'")
        controller.connection.commit()
        print("Wszyscy przypisani pacjenci zostali usunięci z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")


def add_assigned_patients_to_database(data, controller):
    """
    Dodaje listę przypisanych pacjentów do bazy danych za pomocą klasy AssignedPatients.

    :param data: Lista krotek z danymi przypisanych pacjentów.
    :param controller: Obiekt kontrolera bazy danych.
    """
    assigned_patients_model = AssignedPatients(controller)
    assigned_patients_model.create_table()  # Tworzy tabelę `assigned_patients`, jeśli nie istnieje

    for record in data:
        try:
            assigned_patients_model.add_record_by_ids(record[1], record[2])
            print(f"Dodano przypisanie: Pacjent ID {record[1]}, Pracownik {record[2]}.")
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Pacjent ID {record[1]}, Pracownik {record[2]} nie został przypisany.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Pacjent ID {record[1]}, Pracownik {record[2]} nie został przypisany.")


if __name__ == "__main__":
    # Ścieżka do pliku z danymi przypisanych pacjentów
    assigned_patients_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\assigned_patients_list_v2.txt"

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich przypisanych pacjentów
    clear_assigned_patients(db_controller)

    # Wczytanie danych z pliku
    assigned_patients_list = load_assigned_patients_from_file(assigned_patients_file)

    # Dodanie przypisanych pacjentów do bazy danych
    add_assigned_patients_to_database(assigned_patients_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
