from models.room_types import RoomTypes
from controllers.database_controller import DatabaseController
import sqlite3


def load_room_types_from_file(file_path):
    """
    Wczytuje dane typów pomieszczeń z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi typów pomieszczeń.
    :return: Lista krotek z danymi typów pomieszczeń.
    """
    room_type_records = []
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

                room_type_id = int(columns[0])  # ID typu pomieszczenia
                room_type_name = columns[1]  # Nazwa typu pomieszczenia

                room_type_records.append((room_type_id, room_type_name))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return room_type_records


def clear_room_types(controller):
    """
    Usuwa wszystkie typy pomieszczeń z tabeli `room_types` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        controller.connection.execute("DELETE FROM room_types")
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'room_types'")
        controller.connection.commit()
        print("Wszystkie typy pomieszczeń zostały usunięte z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")


def add_room_types_to_database(data, controller):
    """
    Dodaje listę typów pomieszczeń do bazy danych za pomocą klasy RoomTypes.

    :param data: Lista krotek z danymi typów pomieszczeń.
    :param controller: Obiekt kontrolera bazy danych.
    """
    room_types_model = RoomTypes(controller)
    room_types_model.create_table()  # Tworzy tabelę `room_types`, jeśli nie istnieje

    for record in data:
        try:
            room_types_model.create_new_record(record[1])  # Przekazujemy tylko nazwę typu
            print(f"Dodano typ pomieszczenia: {record[1]}.")
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Typ pomieszczenia {record[1]} nie został dodany.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Typ pomieszczenia {record[1]} nie został dodany.")


if __name__ == "__main__":
    # Ścieżka do pliku z danymi typów pomieszczeń
    room_types_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\room_types_list.txt"  # Zmień ścieżkę na odpowiednią

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich typów pomieszczeń
    clear_room_types(db_controller)

    # Wczytanie danych z pliku
    room_types_list = load_room_types_from_file(room_types_file)

    # Dodanie typów pomieszczeń do bazy danych
    add_room_types_to_database(room_types_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
