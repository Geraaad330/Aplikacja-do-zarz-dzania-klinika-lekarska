from models.room_reservations import RoomReservations
from controllers.database_controller import DatabaseController
import sqlite3


def load_reservation_data_from_file(file_path):
    """
    Wczytuje dane rezerwacji pokoi z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi rezerwacji.
    :return: Lista krotek z danymi rezerwacji pokoi.
    """
    reservation_records = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:  # Pomijamy puste linie
                continue
            try:
                # Rozdzielanie danych według przecinków
                columns = [col.strip() for col in line.split(',')]
                if len(columns) != 4:  # Oczekujemy tylko 4 kolumn
                    raise ValueError(f"Niewłaściwa liczba kolumn w wierszu {line_number}.")
                
                # Odczytujemy dane
                reservation_id = int(columns[0])
                fk_room_id = int(columns[1])
                reservation_date = columns[2]
                reservation_time = columns[3]

                reservation_records.append((reservation_id, fk_room_id, reservation_date, reservation_time))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return reservation_records



def clear_reservations(controller):
    """
    Usuwa wszystkie rezerwacje z tabeli `room_reservations` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        controller.connection.execute("DELETE FROM room_reservations")
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'room_reservations'")
        controller.connection.commit()
        print("Wszystkie rezerwacje zostały usunięte z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")


def add_reservations_to_database(data, db_conn):
    """
    Dodaje listę rezerwacji do bazy danych za pomocą klasy RoomReservations.

    :param data: Lista krotek z danymi rezerwacji.
    :param db_conn: Obiekt kontrolera bazy danych.
    """
    reservation_model = RoomReservations(db_conn)
    reservation_model.create_table()  # Tworzy tabelę `room_reservations`, jeśli nie istnieje

    for record in data:
        try:
            # Wywołanie metody `add_reservation` z odpowiednią liczbą argumentów
            reservation_model.add_reservation(
                fk_room_id=record[1],
                reservation_date=record[2],
                reservation_time=record[3],
            )
            print(
                f"Dodano rezerwację: Pokój ID {record[1]}, Data {record[2]}, Czas {record[3]}."
            )
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Rezerwacja nie została dodana.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Rezerwacja nie została dodana.")




if __name__ == "__main__":
    reservations_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\room_reservations_list.txt"

    db_controller = DatabaseController()
    db_controller.connect_to_database()

    clear_reservations(db_controller)

    reservation_list = load_reservation_data_from_file(reservations_file)

    add_reservations_to_database(reservation_list, db_controller)

    db_controller.connection.close()
