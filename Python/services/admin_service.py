
import sqlite3

class AdminService():
    """
    Klasa obsługująca logikę wyświetlania pacjentów w zależności od roli użytkownika.
    """

    def __init__(self, admin_service_controller):
        self.admin_service_controller = admin_service_controller



    def get_all_user_accounts(self):
        """
        Pobiera i formatuje dane wszystkich użytkowników (`users_accounts`),
        w tym dane pracownika (`employee_name`) oraz rolę (`role_name`).
        """
        try:
            # Pobranie wszystkich danych z tabeli users_accounts (bez password_hash)
            query_users = """
                SELECT user_id, employee_id, role_id, username, is_active, created_at, last_login, expired
                FROM users_accounts
            """
            cursor = self.admin_service_controller.db_controller.connection.execute(query_users)
            users_data = [dict(row) for row in cursor.fetchall()]

            if not users_data:
                print("[### ADMIN_SERVICE] Brak danych użytkowników w tabeli users_accounts.")
                return []

            # Pobranie employee_id dla wszystkich użytkowników
            employee_ids = list(set(user["employee_id"] for user in users_data if user["employee_id"] is not None))
            if employee_ids:
                placeholders = ', '.join(['?'] * len(employee_ids))
                query_employees = f"""
                    SELECT employee_id, first_name, last_name FROM employees WHERE employee_id IN ({placeholders})
                """
                cursor = self.admin_service_controller.db_controller.connection.execute(query_employees, employee_ids)
                employees_data = {row["employee_id"]: f"{row['first_name']} {row['last_name']}" for row in cursor.fetchall()}
            else:
                employees_data = {}

            # Pobranie role_id dla wszystkich użytkowników
            role_ids = list(set(user["role_id"] for user in users_data if user["role_id"] is not None))
            if role_ids:
                placeholders = ', '.join(['?'] * len(role_ids))
                query_roles = f"""
                    SELECT role_id, role_name FROM roles WHERE role_id IN ({placeholders})
                """
                cursor = self.admin_service_controller.db_controller.connection.execute(query_roles, role_ids)
                roles_data = {row["role_id"]: row["role_name"] for row in cursor.fetchall()}
            else:
                roles_data = {}

            # Formatowanie wyników
            formatted_users = []
            for user in users_data:
                formatted_users.append({
                    "user_id": user["user_id"],
                    "employee_id": user["employee_id"],
                    "employee_name": employees_data.get(user["employee_id"], "Nieznany pracownik"),
                    "role_id": user["role_id"],
                    "role_name": roles_data.get(user["role_id"], "Nieznana rola"),
                    "username": user["username"],
                    "is_active": user["is_active"],
                    "created_at": user["created_at"],
                    "last_login": user["last_login"],
                    "expired": user["expired"],
                })

            # Debugowanie końcowego wyniku
            # dprint(f"[### ADMIN_SERVICE] Sformatowane dane użytkowników: {formatted_users}")

            return formatted_users

        except sqlite3.OperationalError as op_err:
            print(f"[### ADMIN_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ADMIN_SERVICE] Błąd bazy danych: {db_err}")
            return []
        except KeyError as ke:
            print(f"[### ADMIN_SERVICE] Błąd klucza w danych: {ke}")
            return []
        except TypeError as te:
            print(f"[### ADMIN_SERVICE] Błąd przetwarzania danych: {te}")
            return []


    def get_all_roles(self):
        """
        Pobiera wszystkie dane z tabeli `roles`.

        :return: Lista słowników zawierających dane o rolach.
        """
        try:
            # Pobranie wszystkich danych z tabeli roles
            query = "SELECT * FROM roles"
            cursor = self.admin_service_controller.db_controller.connection.execute(query)
            roles_data = [dict(row) for row in cursor.fetchall()]

            if not roles_data:
                print("[### ADMIN_SERVICE] Brak danych w tabeli roles.")
                return []

            # Debug: Wyświetlenie pobranych ról
            print(f"[### ADMIN_SERVICE] Pobranie ról: {roles_data}")

            return roles_data

        except sqlite3.OperationalError as op_err:
            print(f"[### ADMIN_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ADMIN_SERVICE] Błąd bazy danych: {db_err}")
            return []



    def get_all_assigned_patients(self):
        """
        Pobiera i formatuje dane wszystkich przypisanych pacjentów (`assigned_patients`),
        w tym imię i nazwisko pacjenta (`patient_name`) oraz pracownika (`employee_name`).
        
        :return: Lista słowników zawierających przypisanych pacjentów.
        """
        try:
            # Pobranie wszystkich danych z tabeli assigned_patients
            query_assignments = """
                SELECT assignment_id, fk_patient_id, fk_employee_id, is_active 
                FROM assigned_patients
            """
            cursor = self.admin_service_controller.db_controller.connection.execute(query_assignments)
            assignments_data = [dict(row) for row in cursor.fetchall()]

            if not assignments_data:
                print("[### ADMIN_SERVICE] Brak przypisanych pacjentów w tabeli assigned_patients.")
                return []

            # Pobranie unikalnych employee_id
            employee_ids = list(set(row["fk_employee_id"] for row in assignments_data if row["fk_employee_id"] is not None))
            if employee_ids:
                placeholders = ', '.join(['?'] * len(employee_ids))
                query_employees = f"""
                    SELECT employee_id, first_name, last_name FROM employees WHERE employee_id IN ({placeholders})
                """
                cursor = self.admin_service_controller.db_controller.connection.execute(query_employees, employee_ids)
                employees_data = {row["employee_id"]: f"{row['first_name']} {row['last_name']}" for row in cursor.fetchall()}
            else:
                employees_data = {}

            # Pobranie unikalnych patient_id
            patient_ids = list(set(row["fk_patient_id"] for row in assignments_data if row["fk_patient_id"] is not None))
            if patient_ids:
                placeholders = ', '.join(['?'] * len(patient_ids))
                query_patients = f"""
                    SELECT patient_id, first_name, last_name FROM patients WHERE patient_id IN ({placeholders})
                """
                cursor = self.admin_service_controller.db_controller.connection.execute(query_patients, patient_ids)
                patients_data = {row["patient_id"]: f"{row['first_name']} {row['last_name']}" for row in cursor.fetchall()}
            else:
                patients_data = {}

            # Formatowanie wyników
            formatted_assignments = []
            for assignment in assignments_data:
                formatted_assignments.append({
                    "assignment_id": assignment["assignment_id"],
                    "fk_patient_id": assignment["fk_patient_id"],
                    "patient_name": patients_data.get(assignment["fk_patient_id"], "Nieznany pacjent"),
                    "fk_employee_id": assignment["fk_employee_id"],
                    "employee_name": employees_data.get(assignment["fk_employee_id"], "Nieznany pracownik"),
                    "is_active": assignment["is_active"]
                })

            # Debugowanie końcowego wyniku
            print(f"[### ADMIN_SERVICE] Sformatowane dane przypisanych pacjentów: {formatted_assignments}")

            return formatted_assignments

        except sqlite3.OperationalError as op_err:
            print(f"[### ADMIN_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ADMIN_SERVICE] Błąd bazy danych: {db_err}")
            return []
        except KeyError as ke:
            print(f"[### ADMIN_SERVICE] Błąd klucza w danych: {ke}")
            return []
        except TypeError as te:
            print(f"[### ADMIN_SERVICE] Błąd przetwarzania danych: {te}")
            return []

    def get_all_employee_ids(self):
        """
        Pobiera wszystkie `employee_id` z tabeli `employees`.

        :return: Lista employee_id jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich `employee_id` z tabeli `employees`
            query = "SELECT employee_id FROM employees"
            cursor = self.admin_service_controller.db_controller.connection.execute(query)
            employee_ids = [row["employee_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych employee_id
            print(f"[### ADMIN_SERVICE] Pobranie employee_id z employees: {employee_ids}")

            return employee_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ADMIN_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ADMIN_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_role_ids(self):
        """
        Pobiera wszystkie `role_id` z tabeli `roles`.

        :return: Lista role_id jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich `role_id` z tabeli `roles`
            query = "SELECT role_id FROM roles"
            cursor = self.admin_service_controller.db_controller.connection.execute(query)
            role_ids = [row["role_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych role_id
            print(f"[### ADMIN_SERVICE] Pobranie role_id z roles: {role_ids}")

            return role_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ADMIN_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ADMIN_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_usernames(self):
        """
        Pobiera wszystkie `username` z tabeli `users_accounts`.

        :return: Lista nazw użytkowników jako lista stringów.
        """
        try:
            # Pobranie wszystkich `username` z tabeli `users_accounts`
            query = "SELECT username FROM users_accounts"
            cursor = self.admin_service_controller.db_controller.connection.execute(query)
            usernames = [row["username"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych username
            print(f"[### ADMIN_SERVICE] Pobranie username z users_accounts: {usernames}")

            return usernames

        except sqlite3.OperationalError as op_err:
            print(f"[### ADMIN_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ADMIN_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_employee_ids_from_users_accounts(self):
        """
        Pobiera wszystkie `employee_id` z tabeli `users_accounts`.

        :return: Lista employee_id jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich `employee_id` z tabeli `users_accounts`
            query = "SELECT employee_id FROM users_accounts"
            cursor = self.admin_service_controller.db_controller.connection.execute(query)
            employee_ids = [row["employee_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych employee_id
            print(f"[### ADMIN_SERVICE] Pobranie employee_id z users_accounts: {employee_ids}")

            return employee_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ADMIN_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ADMIN_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_user_ids(self):
        """
        Pobiera wszystkie `user_id` z tabeli `users_accounts`.

        :return: Lista user_id jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich `user_id` z tabeli `users_accounts`
            query = "SELECT user_id FROM users_accounts"
            cursor = self.admin_service_controller.db_controller.connection.execute(query)
            user_ids = [row["user_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych user_id
            print(f"[### ADMIN_SERVICE] Pobranie user_id z users_accounts: {user_ids}")

            return user_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ADMIN_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ADMIN_SERVICE] Błąd bazy danych: {db_err}")
            return []

    def get_all_patient_ids_assigned(self):
        """
        Pobiera wszystkie `fk_patient_id` z tabeli `assigned_patients`.

        :return: Lista fk_patient_id jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich `fk_patient_id` z tabeli `assigned_patients`
            query = "SELECT fk_patient_id FROM assigned_patients"
            cursor = self.admin_service_controller.db_controller.connection.execute(query)
            patient_ids = [row["fk_patient_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych fk_patient_id
            print(f"[### ADMIN_SERVICE] Pobranie fk_patient_id z assigned_patients: {patient_ids}")

            return patient_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ADMIN_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ADMIN_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_patient_id_employee_id_assigned(self):
        """
        Pobiera wszystkie `fk_patient_id` i `fk_employee_id` z tabeli `assigned_patients`.

        :return: Lista słowników zawierających `fk_patient_id` i `fk_employee_id`.
        """
        try:
            # Pobranie wszystkich `fk_patient_id` i `fk_employee_id` z tabeli `assigned_patients`
            query = "SELECT fk_patient_id, fk_employee_id FROM assigned_patients"
            cursor = self.admin_service_controller.db_controller.connection.execute(query)
            assigned_patients = [{"fk_patient_id": row["fk_patient_id"], "fk_employee_id": row["fk_employee_id"]} for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych danych
            print(f"[### ADMIN_SERVICE] Pobranie assigned_patients: {assigned_patients}")

            return assigned_patients

        except sqlite3.OperationalError as op_err:
            print(f"[### ADMIN_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ADMIN_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_assignment_ids(self):
        """
        Pobiera wszystkie `assignment_id` z tabeli `assigned_patients`.

        :return: Lista assignment_id jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich `assignment_id` z tabeli `assigned_patients`
            query = "SELECT assignment_id FROM assigned_patients"
            cursor = self.admin_service_controller.db_controller.connection.execute(query)
            assignment_ids = [row["assignment_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych assignment_id
            print(f"[### ADMIN_SERVICE] Pobranie assignment_id z assigned_patients: {assignment_ids}")

            return assignment_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ADMIN_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ADMIN_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_fk_assignment_ids(self):
        """
        Pobiera wszystkie `fk_assignment_id` z tabeli `appointments`.

        :return: Lista fk_assignment_id jako lista liczb całkowitych.
        """
        try:
            # Pobranie wszystkich `fk_assignment_id` z tabeli `appointments`
            query = "SELECT fk_assignment_id FROM appointments"
            cursor = self.admin_service_controller.db_controller.connection.execute(query)
            fk_assignment_ids = [row["fk_assignment_id"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych fk_assignment_id
            print(f"[### ADMIN_SERVICE] Pobranie fk_assignment_id z appointments: {fk_assignment_ids}")

            return fk_assignment_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ADMIN_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ADMIN_SERVICE] Błąd bazy danych: {db_err}")
            return []


    def get_all_role_names(self):
        """
        Pobiera wszystkie `role_name` z tabeli `roles`.

        :return: Lista role_name jako lista stringów.
        """
        try:
            # Pobranie wszystkich `role_name` z tabeli `roles`
            query = "SELECT role_name FROM roles"
            cursor = self.admin_service_controller.db_controller.connection.execute(query)
            role_names = [row["role_name"] for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych role_name
            print(f"[### ADMIN_SERVICE] Pobranie role_name z roles: {role_names}")

            return role_names

        except sqlite3.OperationalError as op_err:
            print(f"[### ADMIN_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ADMIN_SERVICE] Błąd bazy danych: {db_err}")
            return []

    def get_all_role_user_ids(self):
        """
        Pobiera wszystkie `role_id` i `user_id` z tabeli `users_accounts`.

        :return: Lista słowników zawierających `role_id` i `user_id`.
        """
        try:
            # Pobranie wszystkich `role_id` i `user_id` z tabeli `users_accounts`
            query = "SELECT user_id, role_id FROM users_accounts"
            cursor = self.admin_service_controller.db_controller.connection.execute(query)
            role_user_ids = [{"user_id": row["user_id"], "role_id": row["role_id"]} for row in cursor.fetchall()]

            # Debug: Wyświetlenie pobranych wartości
            print(f"[### ADMIN_SERVICE] Pobranie user_id oraz role_id z users_accounts: {role_user_ids}")

            return role_user_ids

        except sqlite3.OperationalError as op_err:
            print(f"[### ADMIN_SERVICE] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[### ADMIN_SERVICE] Błąd bazy danych: {db_err}")
            return []
