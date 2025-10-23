from models.services import Services
from controllers.database_controller import DatabaseController
import sqlite3


def load_service_data_from_file(file_path):
    """
    Wczytuje dane usług z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi usług.
    :return: Lista krotek z danymi usług.
    """
    service_records = []
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

                # Pobranie danych usługi
                name = columns[1]  # Nazwa usługi
                duration = int(columns[2])  # Czas trwania (w minutach)
                price = int(columns[3])  # Cena (w złotych)

                service_records.append((name, duration, price))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return service_records


def clear_services(controller):
    """
    Usuwa wszystkie usługi z tabeli `services` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        # Usuwanie wszystkich rekordów z tabeli
        controller.connection.execute("DELETE FROM services")
        
        # Resetowanie licznika autoincrement
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'services'")
        
        controller.connection.commit()
        print("Wszystkie usługi zostały usunięte z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")


def add_services_to_database(data, controller):
    """
    Dodaje listę usług do bazy danych za pomocą klasy Services.

    :param data: Lista krotek z danymi usług.
    :param controller: Obiekt kontrolera bazy danych.
    """
    service_model = Services(controller)
    service_model.create_table()  # Tworzy tabelę `services`, jeśli nie istnieje

    for record in data:
        try:
            # Wstawianie danych usługi do bazy
            service_model.create_new_record(*record)
            print(f"Dodano usługę: {record[0]} ({record[1]} min, {record[2]} zł).")
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Usługa {record[0]} nie została dodana.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Usługa {record[0]} nie została dodana.")


if __name__ == "__main__":
    # Ścieżka do pliku z danymi usług
    services_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\services_list.txt"  # Zmień ścieżkę, jeśli plik znajduje się w innej lokalizacji

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich usług
    clear_services(db_controller)

    # Wczytanie danych z pliku
    service_list = load_service_data_from_file(services_file)

    # Dodanie usług do bazy danych
    add_services_to_database(service_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
