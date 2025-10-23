# rooms_controller.py

import sqlite3
from models.rooms import Rooms
from controllers.database_controller import DatabaseController
from controllers.room_types_controller import RoomTypesController


class RoomsController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `rooms`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler `rooms` oraz model zarządzający danymi `rooms`.
        """
        self.db_controller = db_controller
        self.rooms_model = Rooms(db_controller)
        self.room_types_controller = RoomTypesController(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `rooms` w bazie danych.
        """
        try:
            self.rooms_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `rooms`.") from db_error

    def add_room_by_ids(self, room_number: int, floor: int, fk_room_type_id: int) -> bool:
        """
        Dodaje pokój na podstawie ID typu pokoju.
        Zwraca True, jeśli dodanie się powiedzie, False w przypadku błędu.
        """
        try:
            self.rooms_model.add_room_by_ids(room_number, floor, fk_room_type_id)
            return True  # Dodanie powiodło się
        except sqlite3.Error as db_error:
            print(f"[RoomService_add_room_by_ids] Błąd bazy danych: {db_error}")
            return False  # Wystąpił błąd, zwracamy False


    def add_room_by_name(self, room_number: int, floor: int, room_type_name: str):
        """
        Dodaje pokój na podstawie nazwy typu pokoju i zwraca rekord.
        """
        try:
            self.rooms_model.add_room_by_name(room_number, floor, room_type_name)

            # Pobieranie dodanego rekordu
            query = """
            SELECT r.*, rt.room_type AS room_type_name
            FROM rooms r
            LEFT JOIN room_types rt ON r.fk_room_type_id = rt.room_type_id
            WHERE r.room_number = ? AND rt.room_type = ?
            """
            cursor = self.db_controller.connection.execute(query, (room_number, room_type_name))
            return cursor.fetchone()  # Zwraca słownik z danymi rekordu
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania pokoju.") from db_error


    def get_rooms_with_filters(self, filters=None, sort_by=None):
        """
        Pobiera pokoje z tabeli `rooms` z opcjonalnymi filtrami i sortowaniem.
        """
        try:
            return self.rooms_model.get_rooms_with_filters(filters, sort_by)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania rekordów.") from db_error

    def get_rooms_with_room_type_names(self, filters=None, sort_by=None):
        """
        Pobiera pokoje z tabeli `rooms`, zastępując ID typu pokoju nazwą.
        """
        try:
            return self.rooms_model.get_rooms_with_room_type_names(filters, sort_by)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania rekordów z nazwami.") from db_error
        
    def update_room_by_ids(self, room_id: int, data_to_update: dict) -> bool:
        """
        Aktualizuje pokój na podstawie ID.
        :param room_id: ID pokoju do aktualizacji.
        :param data_to_update: Słownik zawierający pola do aktualizacji.
        :return: True, jeśli aktualizacja powiodła się, False w przypadku błędu.
        """
        try:
            # Sprawdzenie, czy jest co aktualizować
            if not data_to_update:
                print("[RoomsController_update_room_by_ids] Brak zmian w danych pokoju. Aktualizacja nie została wykonana.")
                return False  # Brak zmian = brak aktualizacji

            # Przekazanie danych do modelu
            self.rooms_model.update_room_by_ids(room_id, data_to_update)
            return True  # Aktualizacja zakończona sukcesem

        except sqlite3.OperationalError as op_err:
            print(f"[RoomsController_update_room_by_ids] Błąd operacyjny bazy danych: {str(op_err)}")
            return False

        except sqlite3.DatabaseError as db_err:
            print(f"[RoomsController_update_room_by_ids] Błąd bazy danych: {str(db_err)}")
            return False


    def delete_room(self, room_id: int) -> bool:
        """
        Usuwa pokój z tabeli `rooms` na podstawie `room_id`.
        Zwraca True, jeśli operacja się powiodła, False w przypadku błędu.
        """
        try:
            self.rooms_model.delete_room(room_id)
            return True  # Usunięcie zakończone sukcesem
        except sqlite3.Error as db_error:
            print(f"[RoomsController_delete_room] Błąd bazy danych: {db_error}")
            return False  # Wystąpił błąd



    def get_room_by_id(self, room_id):
        """
        Pobiera dane pokoju z modelu na podstawie `room_id`.

        :param room_id: ID pokoju do pobrania.
        :return: Słownik z danymi pokoju lub komunikat błędu.
        """
        try:
            # Sprawdzenie, czy podane `room_id` jest liczbą całkowitą
            if not isinstance(room_id, int):
                raise ValueError(f"Nieprawidłowy format `room_id`: {room_id}. Oczekiwano liczby całkowitej.")

            # Pobranie pokoju z modelu
            room_data = self.rooms_model.get_room_by_id(room_id)

            if room_data is None:
                return f"Pokój o ID {room_id} nie został znaleziony."

            return room_data

        except ValueError as ve:
            print(f"[### ROOMS_CONTROLLER] Błąd wartości: {ve}")
            return f"Błąd wartości: {ve}"

        except TypeError as te:
            print(f"[### ROOMS_CONTROLLER] Błąd typu danych: {te}")
            return f"Błąd typu danych: {te}"