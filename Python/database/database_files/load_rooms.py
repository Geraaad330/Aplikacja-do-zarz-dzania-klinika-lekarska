from models.rooms import Rooms
from controllers.database_controller import DatabaseController
import sqlite3


def load_room_data_from_file(file_path):
    """
    Wczytuje dane pokoi z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi pokoi.
    :return: Lista krotek z danymi pokoi.
    """
    room_records = []
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
                room_id = int(columns[1])
                fk_room_type_id = int(columns[2])
                is_available = int(columns[3])

                room_records.append((room_id, fk_room_type_id, is_available))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return room_records


def clear_rooms(controller):
    """
    Usuwa wszystkie pokoje z tabeli `rooms` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        # Usuwanie wszystkich rekordów z tabeli
        controller.connection.execute("DELETE FROM rooms")
        
        # Resetowanie licznika autoincrement
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'rooms'")
        
        controller.connection.commit()
        print("Wszystkie pokoje zostały usunięte z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")


def add_rooms_to_database(data, controller):
    """
    Dodaje listę pokoi do bazy danych za pomocą klasy Rooms.

    :param data: Lista krotek z danymi pokoi.
    :param controller: Obiekt kontrolera bazy danych.
    """
    room_model = Rooms(controller)
    room_model.create_table()  # Tworzy tabelę `rooms`, jeśli nie istnieje

    for record in data:
        try:
            # Wstawianie danych pokoju do bazy
            room_model.add_room_by_ids(*record)
            print(f"Dodano pokój: ID {record[0]}, Typ {record[1]}.")
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Pokój ID {record[0]} nie został dodany.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Pokój ID {record[0]} nie został dodany.")


if __name__ == "__main__":
    # Ścieżka do pliku z danymi pokoi
    rooms_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\rooms_list.txt"

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich pokoi
    clear_rooms(db_controller)

    # Wczytanie danych z pliku
    room_list = load_room_data_from_file(rooms_file)

    # Dodanie pokoi do bazy danych
    add_rooms_to_database(room_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
