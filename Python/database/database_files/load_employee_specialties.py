from models.employee_specialties import EmployeeSpecialties
from controllers.database_controller import DatabaseController
import sqlite3


def load_employee_specialties_from_file(file_path):
    """
    Wczytuje dane specjalizacji pracowników z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi specjalizacji pracowników.
    :return: Lista krotek z danymi specjalizacji pracowników.
    """
    employee_specialty_records = []
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

                participant_id = int(columns[0])  # ID relacji
                fk_employee_id = int(columns[1])  # ID pracownika
                fk_specialty_id = int(columns[2])  # ID specjalizacji

                employee_specialty_records.append((participant_id, fk_employee_id, fk_specialty_id))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return employee_specialty_records


def clear_employee_specialties(controller):
    """
    Usuwa wszystkie specjalizacje pracowników z tabeli `employee_specialties` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        # Usuwanie wszystkich rekordów z tabeli
        controller.connection.execute("DELETE FROM employee_specialties")
        
        # Resetowanie licznika autoincrement
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'employee_specialties'")
        
        controller.connection.commit()
        print("Wszystkie specjalizacje pracowników zostały usunięte z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")


def add_employee_specialties_to_database(data, controller):
    """
    Dodaje listę specjalizacji pracowników do bazy danych za pomocą klasy EmployeeSpecialties.

    :param data: Lista krotek z danymi specjalizacji pracowników.
    :param controller: Obiekt kontrolera bazy danych.
    """
    employee_specialty_model = EmployeeSpecialties(controller)
    employee_specialty_model.create_table()  # Tworzy tabelę `employee_specialties`, jeśli nie istnieje

    for record in data:
        try:
            employee_specialty_model.add_employee_specialty(record[1], record[2])  # Przekazujemy ID pracownika i ID specjalizacji
            print(f"Dodano specjalizację: Pracownik ID {record[1]}, Specjalizacja ID {record[2]}.")
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Specjalizacja Pracownik ID {record[1]}, Specjalizacja ID {record[2]} nie została dodana.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Specjalizacja Pracownik ID {record[1]}, Specjalizacja ID {record[2]} nie została dodana.")


if __name__ == "__main__":
    # Ścieżka do pliku z danymi specjalizacji pracowników
    employee_specialties_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\employee_specialties_list.txt"

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich specjalizacji pracowników
    clear_employee_specialties(db_controller)

    # Wczytanie danych z pliku
    employee_specialties_list = load_employee_specialties_from_file(employee_specialties_file)

    # Dodanie specjalizacji pracowników do bazy danych
    add_employee_specialties_to_database(employee_specialties_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
