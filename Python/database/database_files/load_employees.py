from models.employees import Employees
from controllers.database_controller import DatabaseController
import sqlite3


def load_employee_data_from_file(file_path):
    """
    Wczytuje dane pracowników z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi pracowników.
    :return: Lista krotek z danymi pracowników.
    """
    employee_records = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:  # Pomijamy puste linie
                continue
            try:
                # Rozdzielanie danych według przecinków
                columns = [col.strip() for col in line.split(',')]
                if len(columns) != 7:
                    raise ValueError(f"Niewłaściwa liczba kolumn w wierszu {line_number}.")
                
                # Odczytujemy wszystkie dane oprócz ID pracownika
                first = columns[1]  # Imię
                last = columns[2]  # Nazwisko
                mail = columns[3]  # Email
                phone_num = columns[4]  # Numer telefonu
                job_title = columns[5]  # Zawód
                medical_flag = int(columns[6])  # Czy personel medyczny (0/1)

                employee_records.append((first, last, mail, phone_num, job_title, medical_flag))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return employee_records


def clear_employees(controller):
    """
    Usuwa wszystkich pracowników z tabeli `employees` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        # Usuwanie wszystkich rekordów z tabeli
        controller.connection.execute("DELETE FROM employees")
        
        # Resetowanie licznika autoincrement
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'employees'")
        
        controller.connection.commit()
        print("Wszyscy pracownicy zostali usunięci z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")





def add_employees_to_database(data, controller):
    """
    Dodaje listę pracowników do bazy danych za pomocą klasy Employees.

    :param data: Lista krotek z danymi pracowników.
    :param controller: Obiekt kontrolera bazy danych.
    """
    employee_model = Employees(controller)
    employee_model.create_table()  # Tworzy tabelę `employees`, jeśli nie istnieje

    for record in data:
        try:
            # Wstawianie danych pracownika do bazy
            employee_model.add_employee(*record)
            print(f"Dodano pracownika: {record[0]} {record[1]} ({record[2]}).")
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Pracownik {record[0]} {record[1]} nie został dodany.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Pracownik {record[0]} {record[1]} nie został dodany.")


if __name__ == "__main__":
    # Ścieżka do pliku z danymi pracowników
    employees_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\employees_list.txt"  # Zmień ścieżkę, jeśli plik znajduje się w innej lokalizacji

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich pracowników
    clear_employees(db_controller)

    # Wczytanie danych z pliku
    employee_list = load_employee_data_from_file(employees_file)

    # Dodanie pracowników do bazy danych
    add_employees_to_database(employee_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
