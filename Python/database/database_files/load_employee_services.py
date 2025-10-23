from models.employee_services import EmployeeServices
from controllers.database_controller import DatabaseController
import sqlite3


def load_employee_services_from_file(file_path):
    """
    Wczytuje dane usług przypisanych pracownikom z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi usług pracowników.
    :return: Lista krotek z danymi usług przypisanych pracownikom.
    """
    employee_service_records = []
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

                record_id = int(columns[0])  # ID relacji
                fk_employee_id = int(columns[1])  # ID pracownika
                fk_service_id = int(columns[2])  # ID usługi

                employee_service_records.append((record_id, fk_employee_id, fk_service_id))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return employee_service_records


def clear_employee_services(controller):
    """
    Usuwa wszystkie usługi przypisane pracownikom z tabeli `employee_services` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        controller.connection.execute("DELETE FROM employee_services")
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'employee_services'")
        controller.connection.commit()
        print("Wszystkie usługi przypisane pracownikom zostały usunięte z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")


def add_employee_services_to_database(data, controller):
    """
    Dodaje listę usług przypisanych pracownikom do bazy danych za pomocą klasy EmployeeServices.

    :param data: Lista krotek z danymi usług przypisanych pracownikom.
    :param controller: Obiekt kontrolera bazy danych.
    """
    employee_services_model = EmployeeServices(controller)
    employee_services_model.create_table()  # Tworzy tabelę `employee_services`, jeśli nie istnieje

    for record in data:
        try:
            employee_services_model.add_employee_service_by_ids(record[1], record[2])  # Przekazujemy ID pracownika i ID usługi
            print(f"Dodano usługę: Pracownik ID {record[1]}, Usługa ID {record[2]}.")
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Usługa Pracownik ID {record[1]}, Usługa ID {record[2]} nie została dodana.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Usługa Pracownik ID {record[1]}, Usługa ID {record[2]} nie została dodana.")


if __name__ == "__main__":
    # Ścieżka do pliku z danymi usług przypisanych pracownikom
    employee_services_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\employee_services_list.txt"

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich usług przypisanych pracownikom
    clear_employee_services(db_controller)

    # Wczytanie danych z pliku
    employee_services_list = load_employee_services_from_file(employee_services_file)

    # Dodanie usług przypisanych pracownikom do bazy danych
    add_employee_services_to_database(employee_services_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
