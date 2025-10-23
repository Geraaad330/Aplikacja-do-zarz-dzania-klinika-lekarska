# specialties_controller.py

import sqlite3
from models.specialties import Specialties
from controllers.database_controller import DatabaseController


class SpecialtiesController:
    """
    Kontroler odpowiedzialny za logikę biznesową dla tabeli `specialties`.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje kontroler specjalności oraz model zarządzający danymi specjalności.
        """
        self.db_controller = db_controller
        self.specialties_model = Specialties(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `specialties` w bazie danych.
        """
        try:
            self.specialties_model.create_table()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas tworzenia tabeli `specialties`.") from db_error

    def add_specialty(self, specialty_name, is_active):
        """
        Dodaje nową specjalność do tabeli `specialties`.
        """
        try:
            self.specialties_model.create_new_record(specialty_name, is_active)
            return {"success": True}  # Dodano poprawne zwracanie wartości
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas dodawania nowej specjalności.") from db_error


    def get_specialty_name_by_id(self, specialty_id):
        """
        Pobiera nazwę specjalizacji na podstawie specialty_id za pomocą modelu.

        Args:
            specialty_id (int): ID specjalizacji.

        Returns:
            str: Nazwa specjalizacji, jeśli istnieje, w przeciwnym razie None.
        """
        return self.specialties_model.get_specialty_name_by_id(specialty_id)



    def get_all_specialties(self):
        """
        Pobiera wszystkie rekordy z tabeli `specialties`.
        """
        try:
            if not self.db_controller.connection:
                raise RuntimeError("Brak połączenia z bazą danych.")
            return self.specialties_model.get_records()
        except Exception as e:
            raise RuntimeError(f"Błąd podczas pobierania specjalności: {e}") from e

    def get_specialties_with_filters(self, filters=None, sort_by=None):
        """
        Pobiera specjalności na podstawie filtrów i sortowania.
        """
        try:
            # Jeśli filtry to None, ustaw pustą listę
            if filters is None:
                filters = []

            # Jeśli filtry to słownik, konwertujemy go na listę z domyślnym operatorem "="
            if isinstance(filters, dict):
                filters = [{"column": key, "value": value, "operator": "="} for key, value in filters.items()]
            else:
                # Jeśli filtry to lista, dodajemy brakujące operatory
                for filter_item in filters:
                    filter_item.setdefault("operator", "=")

            return self.specialties_model.get_records(filters=filters, sort_by=sort_by)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania specjalności.") from db_error




    def update_specialty(self, specialty_id, updates):
        """
        Aktualizuje specjalność na podstawie ID.
        """
        try:
            self.specialties_model.update_record(specialty_id, updates)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas aktualizacji specjalności.") from db_error

    def delete_specialty(self, specialty_id):
        """
        Usuwa specjalność na podstawie ID.
        """
        try:
            self.specialties_model.delete_record(specialty_id)
        except ValueError as validation_error:
            raise ValueError(f"Błąd walidacji: {validation_error}") from validation_error
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas usuwania specjalności.") from db_error

    def count_specialties_for_all_professions(self):
        """
        Zlicza specjalności dla każdego dostępnego zawodu.
        """
        try:
            return self.specialties_model.count_specialties_for_all_professions()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas zliczania specjalności dla wszystkich zawodów.") from db_error

    def get_available_professions(self):
        """
        Pobiera listę dostępnych zawodów z bazy danych.
        """
        try:
            return self.specialties_model.get_available_professions()
        except sqlite3.Error as db_error:
            raise RuntimeError("Błąd bazy danych podczas pobierania listy zawodów.") from db_error

    def count_specialties_for_profession(self, profession):
        """
        Zlicza specjalności powiązane z danym zawodem.
        """
        query = """
        SELECT specialties.specialty_name
        FROM specialties
        JOIN employee_specialties ON specialties.specialty_id = employee_specialties.specialty_id
        JOIN employees ON employee_specialties.employee_id = employees.employee_id
        WHERE employees.profession = ?
        ORDER BY specialties.specialty_name ASC
        """
        try:
            results = self.db_controller.connection.execute(query, (profession,)).fetchall()
            return [{"specialty_name": row["specialty_name"]} for row in results]
        except Exception as e:
            raise RuntimeError(f"Nie udało się zliczyć specjalności dla zawodu '{profession}': {e}") from e

    def get_all_specialty_names(self):
        """
        Pobiera wszystkie dostępne nazwy specjalności.

        :return: Lista specjalności.
        :raises ValueError: Jeśli nie znaleziono żadnych rekordów.
        :raises RuntimeError: W przypadku błędu bazy danych.
        """
        try:
            specialty_names = self.specialties_model.get_all_specialty_names()
            if not specialty_names:
                raise ValueError("Brak dostępnych specjalności w bazie danych.")
            return specialty_names
        except sqlite3.Error as db_error:
            raise RuntimeError(f"Błąd bazy danych podczas pobierania specjalności: {db_error}") from db_error
        
    def get_all_specialty_ids(self):
        """
        Pobiera wszystkie `specialty_id` z tabeli `specialties`.

        :return: Lista specialty_id.
        :raises RuntimeError: Jeśli wystąpi błąd bazy danych.
        """
        try:
            return self.specialties_model.get_all_specialty_ids()
        except RuntimeError as re:
            print(f"[SpecialtiesController] Błąd pobierania specialty_id: {re}")
            return []
    
    def get_specialty_by_id(self, specialty_id: int):
        """
        Pobiera wszystkie kolumny rekordu w tabeli `specialties` dla podanego specialty_id.

        :param specialty_id: ID specjalności.
        :return: Słownik z danymi specjalności lub None, jeśli nie znaleziono.
        :raises ValueError: Jeśli specialty_id jest niepoprawne.
        :raises RuntimeError: Jeśli wystąpi błąd bazy danych.
        """
        try:
            return self.specialties_model.get_specialty_by_id(specialty_id)
        except ValueError as ve:
            print(f"[SpecialtiesController] Błąd wartości: {ve}")
            raise
        except RuntimeError as re:
            print(f"[SpecialtiesController] Błąd bazy danych: {re}")
            raise