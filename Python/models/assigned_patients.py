# assigned_patients.py

import sqlite3
from controllers.database_controller import DatabaseController
from controllers.users_accounts_controller import UsersAccountsController
from controllers.patients_controller import PatientController
from validators.assigned_patients_model_validation import (
    validate_name,
    validate_user_name,
    validate_patient_exists,
    validate_user_exists,
    # validate_unique_assignment,
    validate_operator_and_value,
    validate_filters_and_sorting
)


def get_valid_columns(db_controller, table_name: str) -> list:
    """
    Pobiera listę kolumn dla podanej tabeli z bazy danych.
    :param db_controller: Obiekt kontrolera bazy danych.
    :param table_name: Nazwa tabeli.
    :return: Lista nazw kolumn.
    """
    db_controller.ensure_connection()
    query = f"PRAGMA table_info({table_name})"
    cursor = db_controller.connection.execute(query)
    return [row["name"] for row in cursor.fetchall()]


class AssignedPatients:
    """
    Klasa zarządzająca tabelą `assigned_patients` dla operacji CRUD.
    """

    def __init__(self, db_controller: DatabaseController):
        """
        Inicjalizuje obiekt klasy AssignedPatients.
        """
        self.db_controller = db_controller
        self.users_accounts_controller = UsersAccountsController(db_controller)
        self.patient_controller = PatientController(db_controller)

    def create_table(self):
        """
        Tworzy tabelę `assigned_patients` zgodnie z SQL.
        """
        try:
            self.db_controller.ensure_connection()
            if not self.db_controller.table_exists("assigned_patients"):
                query = """
                CREATE TABLE IF NOT EXISTS assigned_patients (
                    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fk_patient_id INTEGER NOT NULL,
                    fk_employee_id INTEGER NOT NULL,
                    FOREIGN KEY (fk_patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
                    FOREIGN KEY (fk_employee_id) REFERENCES users_accounts(user_id) ON DELETE CASCADE,
                    UNIQUE (fk_patient_id, fk_employee_id)
                )
                """
                self.db_controller.connection.execute(query)
                self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas tworzenia tabeli: {e}") from e

    def add_record_by_ids(self, fk_patient_id: int, fk_employee_id: int, is_active=True):
        """
        Dodaje nowy rekord na podstawie ID pacjenta (fk_patient_id) i użytkownika (fk_employee_id).
        """
        try:
            # Walidacje
            # validate_unique_assignment(self.db_controller, fk_patient_id, fk_employee_id)

            self.db_controller.ensure_connection()
            query = """
            INSERT INTO assigned_patients (fk_patient_id, fk_employee_id, is_active)
            VALUES (?, ?, ?)
            """
            self.db_controller.connection.execute(query, (fk_patient_id, fk_employee_id, is_active))
            self.db_controller.connection.commit()
        except sqlite3.IntegrityError as e:
            raise RuntimeError(f"Błąd integralności danych: {e}") from e

    def add_record_by_names(self, patient_first_name: str, patient_last_name: str, user_name: str):
        """
        Dodaje nowy rekord na podstawie nazw pacjenta i użytkownika.
        """
        # Walidacje
        validate_name(patient_first_name)
        validate_name(patient_last_name)
        validate_user_name(user_name)
        validate_patient_exists(self.patient_controller, patient_first_name, patient_last_name)
        validate_user_exists(self.users_accounts_controller, user_name)

        fk_patient_id = self.get_patient_id(patient_first_name, patient_last_name)
        fk_employee_id = self.get_user_id(user_name)

        self.add_record_by_ids(fk_patient_id, fk_employee_id)



    def get_patient_id(self, first_name: str, last_name: str) -> int:
        """
        Pobiera ID pacjenta na podstawie imienia i nazwiska.

        :param first_name: Imię pacjenta.
        :param last_name: Nazwisko pacjenta.
        :return: ID pacjenta.
        """
        results = self.patient_controller.advanced_filter_patients(first_name=first_name, last_name=last_name)
        if not results:
            raise KeyError(f"Pacjent o imieniu '{first_name}' i nazwisku '{last_name}' nie został znaleziony.")
        return results[0]["patient_id"]

    def get_user_id(self, username: str) -> int:
        """
        Pobiera ID użytkownika na podstawie nazwy użytkownika.

        :param username: Nazwa użytkownika.
        :return: ID użytkownika.
        """
        results = self.users_accounts_controller.get_users_with_filters(
            filters=[{"column": "username", "operator": "=", "value": username}]
        )
        if not results:
            raise KeyError(f"Użytkownik o nazwie '{username}' nie został znaleziony.")
        return results[0]["user_id"]




    def get_records_with_filters(self, filters=None, sort_by=None):
        """
        Pobiera rekordy z tabeli `assigned_patients` z opcjonalnymi filtrami i sortowaniem.
        """
        try:
            # Definicja dozwolonych kolumn i aliasów
            valid_columns = ["assignment_id", "fk_patient_id", "fk_employee_id", "users_accounts.username", "patients.first_name", "patients.last_name"]
            alias_map = {
                "u.username": "users_accounts.username",
                "p.first_name": "patients.first_name",
                "p.last_name": "patients.last_name",
            }

            # Walidacja filtrów i sortowania
            validate_filters_and_sorting(filters, sort_by, valid_columns, alias_map)

            # Walidacja operatorów i wartości w filtrach
            if filters:
                for filter_item in filters:
                    operator = filter_item["operator"]
                    value = filter_item["value"]

                    # Użycie walidacji operatora i wartości
                    validate_operator_and_value(operator, value)

            # Tworzenie zapytania SQL
            self.db_controller.ensure_connection()
            query_conditions, values = self.db_controller.build_filters(filters, sort_by)
            query = f"""
            SELECT 
                ap.assignment_id, ap.fk_patient_id, ap.fk_employee_id, 
                u.username AS username, 
                p.first_name AS patient_first_name, 
                p.last_name AS patient_last_name
            FROM assigned_patients ap
            JOIN users_accounts u ON ap.fk_employee_id = u.user_id
            JOIN patients p ON ap.fk_patient_id = p.patient_id
            WHERE {query_conditions}
            """

            cursor = self.db_controller.connection.execute(query, values)
            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów: {e}") from e









    def get_record_by_patient_and_user_ids(self, fk_patient_id: int, fk_employee_id: int):
        """
        Pobiera dane dla konkretnego pacjenta i użytkownika na podstawie ich ID.

        :param fk_patient_id: ID pacjenta.
        :param fk_employee_id: ID użytkownika.
        :return: Rekord jako słownik lub None, jeśli nie znaleziono.
        """
        try:
            self.db_controller.ensure_connection()
            query = """
            SELECT * FROM assigned_patients
            WHERE fk_patient_id = ? AND fk_employee_id = ?
            """
            cursor = self.db_controller.connection.execute(query, (fk_patient_id, fk_employee_id))
            record = cursor.fetchone()
            return dict(record) if record else None
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordu: {e}") from e

    def get_records_with_names(self, filters=None, sort_by=None):
        """
        Pobiera dane z tabeli `assigned_patients`, zastępując ID nazwami użytkowników i pacjentów.

        :param filters: Lista filtrów w formacie [{"column": "fk_patient_id", "operator": "=", "value": 1}]
        :param sort_by: Lista sortowania w formacie [("user_name", "ASC")]
        :return: Lista rekordów w formie listy słowników z nazwami zamiast ID.
        """
        try:
            self.db_controller.ensure_connection()
            query_conditions, values = self.db_controller.build_filters(filters, sort_by)
            query = f"""
            SELECT 
                ap.assignment_id,
                p.first_name || ' ' || p.last_name AS patient_name,
                ua.username AS user_name
            FROM assigned_patients ap
            JOIN patients p ON ap.fk_patient_id = p.patient_id
            JOIN users_accounts ua ON ap.fk_employee_id = ua.user_id
            WHERE {query_conditions}
            """
            cursor = self.db_controller.connection.execute(query, values)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas pobierania rekordów z nazwami: {e}") from e



    def update_record_by_ids(self, assignment_id: int, **update_data) -> bool:
        """
        Aktualizuje rekord w tabeli `assigned_patients` na podstawie `assignment_id` i dostarczonych wartości.

        :param assignment_id: ID przypisania do aktualizacji.
        :param update_data: Słownik zawierający klucze i wartości do aktualizacji.
        :return: True, jeśli operacja się powiodła, False w przypadku błędu.
        """
        try:
            if not update_data:
                print("[### ASSIGNED_PATIENTS_MODEL] Brak danych do aktualizacji.")
                return False  # Brak aktualizacji

            self.db_controller.ensure_connection()

            # **Sprawdzenie, czy rekord istnieje**
            query_check = "SELECT assignment_id FROM assigned_patients WHERE assignment_id = ?"
            record = self.db_controller.connection.execute(query_check, (assignment_id,)).fetchone()
            if not record:
                print(f"[### ASSIGNED_PATIENTS_MODEL] Nie znaleziono rekordu o ID {assignment_id} do aktualizacji.")
                return False

            # **Budowanie zapytania aktualizacyjnego**
            set_clause = ", ".join([f"{key} = ?" for key in update_data.keys()])
            query = f"UPDATE assigned_patients SET {set_clause} WHERE assignment_id = ?"
            params = list(update_data.values()) + [assignment_id]

            cursor = self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()

            return cursor.rowcount > 0  # True jeśli aktualizacja się powiodła, False w przeciwnym razie

        except sqlite3.OperationalError as op_err:
            print(f"[### ASSIGNED_PATIENTS_MODEL] Błąd operacyjny bazy danych: {op_err}")
            return False
        except sqlite3.DatabaseError as db_err:
            print(f"[### ASSIGNED_PATIENTS_MODEL] Błąd bazy danych: {db_err}")
            return False





    def update_record_by_names(self, assignment_id: int, patient_first_name: str = None, patient_last_name: str = None, user_name: str = None):
        """
        Aktualizuje rekord na podstawie assignment_id, ustawiając nowe wartości dla pacjenta (first_name, last_name) i/lub użytkownika (user_name).

        :param assignment_id: ID przypisania do zaktualizowania.
        :param patient_first_name: Imię pacjenta (opcjonalnie).
        :param patient_last_name: Nazwisko pacjenta (opcjonalnie).
        :param user_name: Nazwa użytkownika (opcjonalnie).
        """
        try:
            fk_patient_id = None
            fk_employee_id = None

            if patient_first_name and patient_last_name:
                fk_patient_id = self.get_patient_id(patient_first_name, patient_last_name)
            if user_name:
                fk_employee_id = self.get_user_id(user_name)

            self.update_record_by_ids(assignment_id, fk_patient_id=fk_patient_id, fk_employee_id=fk_employee_id)
        except Exception as e:
            raise RuntimeError(f"Błąd podczas aktualizacji rekordu po nazwach: {e}") from e






    def delete_record_by_id(self, assignment_id: int):
        """
        Usuwa rekord na podstawie assignment_id.
        """
        try:
            self.db_controller.ensure_connection()
            query = "DELETE FROM assigned_patients WHERE assignment_id = ?"
            self.db_controller.connection.execute(query, (assignment_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordu: {e}") from e



    def delete_record_by_assignment_id(self, assignment_id: int):
        """
        Usuwa rekord z tabeli assigned_patients na podstawie assignment_id.
        """
        try:
            self.db_controller.ensure_connection()
            query = """
            DELETE FROM assigned_patients
            WHERE assignment_id = ?
            """
            self.db_controller.connection.execute(query, (assignment_id,))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordu: {e}") from e


    def delete_records_by_patient_or_user_ids(self, fk_patient_id: int = None, fk_employee_id: int = None):
        """
        Usuwa wszystkie rekordy związane z fk_patient_id i/lub fk_employee_id.

        :param fk_patient_id: ID pacjenta (opcjonalnie).
        :param fk_employee_id: ID użytkownika (opcjonalnie).
        """
        try:
            self.db_controller.ensure_connection()
            conditions = []
            params = []
            if fk_patient_id is not None:
                conditions.append("fk_patient_id = ?")
                params.append(fk_patient_id)
            if fk_employee_id is not None:
                conditions.append("fk_employee_id = ?")
                params.append(fk_employee_id)
            if not conditions:
                raise ValueError("Musisz podać co najmniej fk_patient_id lub fk_employee_id.")
            query = f"DELETE FROM assigned_patients WHERE {' OR '.join(conditions)}"
            self.db_controller.connection.execute(query, params)
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordów: {e}") from e
        
    def delete_record_by_ids(self, fk_patient_id: int, fk_employee_id: int):
        """
        Usuwa rekord z tabeli assigned_patients na podstawie fk_patient_id i fk_employee_id.
        """
        try:
            # Walidacje
            query_check = """
            SELECT assignment_id
            FROM assigned_patients
            WHERE fk_patient_id = ? AND fk_employee_id = ?
            """
            record = self.db_controller.connection.execute(query_check, (fk_patient_id, fk_employee_id)).fetchone()
            if not record:
                raise ValueError("Nie znaleziono rekordu do usunięcia.")

            query_delete = """
            DELETE FROM assigned_patients
            WHERE fk_patient_id = ? AND fk_employee_id = ?
            """
            self.db_controller.connection.execute(query_delete, (fk_patient_id, fk_employee_id))
            self.db_controller.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordu: {e}") from e



    def delete_record_by_names(self, patient_first_name: str = None, patient_last_name: str = None, user_name: str = None):
        """
        Usuwa rekord z tabeli `assigned_patients` na podstawie nazw pacjenta i/lub użytkownika.
        """
        fk_patient_id = None
        fk_employee_id = None

        if patient_first_name and patient_last_name:
            try:
                fk_patient_id = self.get_patient_id(patient_first_name, patient_last_name)
            except KeyError:
                pass  # Pacjent nie istnieje
        if user_name:
            try:
                fk_employee_id = self.get_user_id(user_name)
            except KeyError:
                pass  # Użytkownik nie istnieje

        if fk_patient_id is None and fk_employee_id is None:
            raise KeyError("Nie znaleziono użytkownika lub pacjenta dla podanych danych.")

        try:
            self.delete_record_by_ids(fk_patient_id=fk_patient_id, fk_employee_id=fk_employee_id)
        except Exception as e:
            raise RuntimeError(f"Błąd podczas usuwania rekordu po nazwach: {e}") from e




    def get_assigned_patients_by_employee_id(self, fk_employee_id: int) -> list:
        """
        Pobiera wszystkie fk_patient_id przypisane do podanego fk_employee_id.
        """
        try:
            query = """
            SELECT fk_patient_id
            FROM assigned_patients
            WHERE fk_employee_id = ?
            """
            self.db_controller.ensure_connection()
            cursor = self.db_controller.connection.execute(query, (fk_employee_id,))
            results = [{"fk_patient_id": row["fk_patient_id"]} for row in cursor.fetchall()]

            # print(f"[model assigned_patients] Pobrano przypisanych pacjentów dla user_id {user_id}: {results}")

            if not results:
                print(f"[model assigned_patients] Nie znaleziono przypisanych pacjentów dla user_id {fk_employee_id}.")
                raise ValueError(f"Brak przypisanych pacjentów dla user_id {fk_employee_id}.")

            # print(f"[model assigned_patients] Przypisani pacjenci dla user_id {user_id}: {results}")
            return results

        except sqlite3.Error as e:
            print(f"[model assigned_patients] Błąd bazy danych podczas pobierania pacjentów dla user_id {fk_employee_id}: {e}")
            raise RuntimeError(f"Błąd bazy danych podczas pobierania przypisanych pacjentów: {e}") from e


    def get_all_assigned_patients(self):
        """
        Pobiera wszystkie rekordy z tabeli assigned_patients.
        """
        try:
            query = "SELECT * FROM assigned_patients"
            cursor = self.db_controller.connection.cursor()
            cursor.execute(query)
            assigned_patients = cursor.fetchall()

            if not assigned_patients:
                print("[AssignedPatientsModel] Brak przypisanych pacjentów w bazie.")
                return []

            return assigned_patients

        except sqlite3.OperationalError as e:
            raise RuntimeError(f"Błąd operacyjny bazy danych: {e}") from e

        except sqlite3.Error as e:
            raise RuntimeError(f"Błąd ogólny bazy danych: {e}") from e


    # assigned_patients_model.py
    def get_employee_id_by_assignment_id(self, assignment_id: int) -> int:
        """
        Pobiera fk_employee_id na podstawie podanego assignment_id z tabeli assigned_patients.
        
        :param assignment_id: ID przypisania do weryfikacji
        :return: ID pracownika powiązanego z przypisaniem
        :raises RuntimeError: Błąd operacji bazodanowej
        :raises ValueError: Brak przypisania dla podanego ID
        """
        try:
            query = "SELECT fk_employee_id FROM assigned_patients WHERE assignment_id = ?"
            self.db_controller.ensure_connection()
            cursor = self.db_controller.connection.execute(query, (assignment_id,))
            result = cursor.fetchone()

            if not result:
                print(f"[model assigned_patients] Brak przypisania dla assignment_id {assignment_id}")
                raise ValueError(f"Nie znaleziono przypisania o ID {assignment_id}")

            employee_id = result["fk_employee_id"]
            print(f"[model assigned_patients] Znaleziono employee_id {employee_id} dla assignment_id {assignment_id}")
            return employee_id

        except sqlite3.Error as e:
            error_msg = f"Błąd bazy danych podczas wyszukiwania przypisania {assignment_id}: {str(e)}"
            print(f"[model assigned_patients] {error_msg}")
            raise RuntimeError(error_msg) from e
        

    def get_assigned_patient_by_id(self, assignment_id):
        """
        Pobiera dane przypisanego pacjenta na podstawie `assignment_id`.

        :param assignment_id: ID przypisania pacjenta.
        :return: Słownik z danymi przypisania lub None, jeśli nie znaleziono.
        """
        try:
            # Sprawdzenie, czy assignment_id to liczba całkowita
            if not isinstance(assignment_id, int):
                raise ValueError(f"Nieprawidłowy format `assignment_id`: {assignment_id}. Oczekiwano liczby całkowitej.")

            # Pobranie danych przypisania pacjenta
            query = """
                SELECT assignment_id, fk_patient_id, fk_employee_id, is_active 
                FROM assigned_patients 
                WHERE assignment_id = ?
            """
            cursor = self.db_controller.connection.execute(query, (assignment_id,))
            result = cursor.fetchone()

            if result is None:
                return None

            return {
                "assignment_id": result["assignment_id"],
                "fk_patient_id": result["fk_patient_id"],
                "fk_employee_id": result["fk_employee_id"],
                "is_active": result["is_active"]
            }

        except sqlite3.OperationalError as op_err:
            print(f"[### ASSIGNED_PATIENTS_MODEL] Błąd operacyjny bazy danych: {op_err}")
            return None
        except sqlite3.DatabaseError as db_err:
            print(f"[### ASSIGNED_PATIENTS_MODEL] Błąd bazy danych: {db_err}")
            return None
        except ValueError as ve:
            print(f"[### ASSIGNED_PATIENTS_MODEL] Błąd wartości: {ve}")
            return None
