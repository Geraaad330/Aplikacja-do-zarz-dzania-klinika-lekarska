# room_reservations_controller.py

import sqlite3
from models.room_reservations import RoomReservations
from controllers.database_controller import DatabaseController


class RoomReservationsController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `room_reservations`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler `room_reservations` oraz model zarządzający danymi `room_reservations`.

        Args:
            db_controller (DatabaseController): Instancja kontrolera bazy danych.
        """
        self.db_controller = db_controller
        self.room_reservations_model = RoomReservations(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `room_reservations` w bazie danych.
        """
        try:
            self.room_reservations_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `room_reservations`.") from db_error

    def add_reservation(self, fk_room_id, reservation_date, reservation_time):
        """
        Dodaje nową rezerwację do tabeli `room_reservations`.

        Args:
            fk_room_id (int): ID pokoju.
            fk_appointment_id (int): ID wizyty.
            fk_meeting_id (int | None): ID spotkania.
            reservation_date (str): Data rezerwacji.
            reservation_time (str): Czas rezerwacji.

        Returns:
            int: ID nowo dodanej rezerwacji.
        """
        try:
            return self.room_reservations_model.add_reservation(
                fk_room_id, reservation_date, reservation_time
            )
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania rezerwacji.") from db_error

    def get_reservations(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `room_reservations` z opcjonalnymi filtrami i sortowaniem.

        Args:
            filters (list): Lista filtrów w formacie [{"column": ..., "operator": ..., "value": ...}].
            sort_by (list): Lista sortowania w formacie [{"column": ..., "direction": ...}].

        Returns:
            list[dict]: Lista rezerwacji jako słowniki.
        """
        try:
            return self.room_reservations_model.get_reservations(filters, sort_by)
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania rezerwacji.") from db_error

    def update_reservation(self, reservation_id: int, fk_room_id: int = None, reservation_date: str = None, reservation_time: str = None) -> bool:
        """
        Wywołuje metodę modelu do aktualizacji rezerwacji.

        :param reservation_id: ID rezerwacji do aktualizacji.
        :param fk_room_id: Nowe ID pokoju (opcjonalnie).
        :param reservation_date: Nowa data rezerwacji (opcjonalnie, format YYYY-MM-DD).
        :param reservation_time: Nowy czas rezerwacji (opcjonalnie, format HH:MM-HH:MM).
        :return: True, jeśli aktualizacja się powiodła, False w przypadku błędu.
        """
        try:
            self.room_reservations_model.update_reservation(
                reservation_id, fk_room_id, reservation_date, reservation_time
            )
            return True  # Aktualizacja zakończona sukcesem

        except RuntimeError as err:
            print(f"[RoomReservationsController_update_reservation] Błąd aktualizacji: {err}")
            return False  # Wystąpił błąd podczas aktualizacji


    def delete_reservation(self, reservation_id: int) -> bool:
        """
        Usuwa rezerwację na podstawie `reservation_id`.

        Args:
            reservation_id (int): ID rezerwacji do usunięcia.

        Returns:
            bool: True, jeśli operacja się powiodła, False w przypadku błędu.
        """
        try:
            self.room_reservations_model.delete_reservation(reservation_id)
            return True  # Usunięcie zakończone sukcesem
        except sqlite3.Error as db_error:
            print(f"[RoomReservationsController_delete_reservation] Błąd bazy danych: {db_error}")
            return False  # Wystąpił błąd
