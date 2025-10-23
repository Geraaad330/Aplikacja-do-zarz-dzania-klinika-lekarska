# room_types_controller.py

import sqlite3
from models.room_types import RoomTypes
from controllers.database_controller import DatabaseController


class RoomTypesController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `room_types`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler `room_types` oraz model zarządzający danymi spotkań.
        """
        self.db_controller = db_controller
        self.room_types_model = RoomTypes(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `room_types` w bazie danych.
        """
        try:
            self.room_types_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `room_types`.") from db_error

    def add_room_type(self, room_type: str):
        """
        Dodaje nowy typ pokoju do tabeli `room_types` i zwraca rekord.
        """
        try:
            self.room_types_model.create_new_record(room_type)

            # Pobieranie dodanego rekordu
            query = "SELECT * FROM room_types WHERE room_type = ?"
            cursor = self.db_controller.connection.execute(query, (room_type,))
            return cursor.fetchone()  # Zwraca słownik z danymi rekordu
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania nowego typu pokoju.") from db_error


    def get_all_room_types(self):
        """
        Pobiera wszystkie rekordy z tabeli `room_types`.
        """
        try:
            if not self.db_controller.connection:
                raise RuntimeError("Brak połączenia z bazą danych.")
            return self.room_types_model.get_records()
        except Exception as e:
            raise RuntimeError(f"Błąd podczas pobierania typów spotkań: {e}") from e

    def get_room_types_with_filters(self, filters=None, sort_by=None):
        """
        Pobiera typy spotkań na podstawie filtrów i sortowania.
        """
        try:
            return self.room_types_model.get_records(filters=filters, sort_by=sort_by)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania typów spotkań.") from db_error


    def update_room_type(self, room_type_id: int, new_room_type: str) -> bool:
        """
        Wywołuje metodę modelu do aktualizacji nazwy typu pokoju.

        :param room_type_id: ID typu pokoju do aktualizacji.
        :param new_room_type: Nowa nazwa typu pokoju.
        :return: True, jeśli aktualizacja się powiodła, False w przypadku błędu.
        """
        try:
            self.room_types_model.update_room_type(room_type_id, new_room_type)
            return True  # Aktualizacja zakończona sukcesem

        except RuntimeError as err:
            print(f"[RoomTypesController_update_room_type] Błąd aktualizacji: {err}")
            return False

    def delete_room_type(self, room_type_id: int) -> bool:
        """
        Usuwa typ pokoju na podstawie ID.
        
        :param room_type_id: ID typu pokoju do usunięcia.
        :return: True, jeśli usunięcie się powiodło, False w przypadku błędu.
        """
        try:
            self.room_types_model.delete_record(room_type_id)
            return True  # Sukces

        except RuntimeError as runtime_error:
            print(f"[RoomTypesController_deleteRoomType] Błąd: {runtime_error}")
            return False  # Wystąpił błąd aplikacji

        except sqlite3.Error as db_error:
            print(f"[RoomTypesController_deleteRoomType] Błąd bazy danych: {db_error}")
            return False  # Wystąpił błąd bazy danych
