import sqlite3

class EmployeeService():
    """
    Klasa obsługująca logikę wyświetlania pacjentów w zależności od roli użytkownika.
    """

    def __init__(self, employee_service_controller):
        self.employee_service_controller = employee_service_controller



    def get_services_and_specialties_table(self):
        """
        Pobiera dane z tabel services i specialties.
        
        Returns:
            dict: Zawiera dwie listy - services i specialties, każda jako lista słowników.
        """
        try:
            # Pobranie wszystkich danych z tabeli services
            query_services = "SELECT * FROM services"
            cursor = self.employee_service_controller.db_controller.connection.execute(query_services)
            services_data = [dict(row) for row in cursor.fetchall()]
            # print(f"[### EMPLOYEE_SERVICE] Pobranie danych z tabeli services: {services_data}")

            # Pobranie wszystkich danych z tabeli specialties
            query_specialties = "SELECT * FROM specialties"
            cursor = self.employee_service_controller.db_controller.connection.execute(query_specialties)
            specialties_data = [dict(row) for row in cursor.fetchall()]
            # print(f"[### EMPLOYEE_SERVICE] Pobranie danych z tabeli specialties: {specialties_data}")

            # Zwrócenie wyników jako słownik
            return {
                "services": services_data,
                "specialties": specialties_data
            }

        except AttributeError as attr_error:
            print(f"[### EMPLOYEE_SERVICE] Błąd atrybutu: {str(attr_error)}")
            return {"services": [], "specialties": []}
        except TypeError as type_error:
            print(f"[### EMPLOYEE_SERVICE] Błąd typu danych: {str(type_error)}")
            return {"services": [], "specialties": []}


    def get_formatted_employee_services(self):
        """
        Pobiera dane z tabeli employee_services, employees i services,
        formatuje je, aby dodać kolumny first_name, last_name oraz service_type.

        Returns:
            list: Lista słowników zawierających sformatowane dane.
        """
        try:
            # Pobranie danych z tabeli employee_services
            query_employee_services = "SELECT * FROM employee_services"
            cursor = self.employee_service_controller.db_controller.connection.execute(query_employee_services)
            employee_services_data = [dict(row) for row in cursor.fetchall()]
            # print(f"[### EMPLOYEE_SERVICE] Dane z tabeli employee_services: {employee_services_data}")

            # Pobranie danych z tabeli employees
            query_employees = "SELECT employee_id, first_name, last_name FROM employees"
            cursor = self.employee_service_controller.db_controller.connection.execute(query_employees)
            employees_data = {row["employee_id"]: {"first_name": row["first_name"], "last_name": row["last_name"]} for row in cursor.fetchall()}
            # print(f"[### EMPLOYEE_SERVICE] Dane z tabeli employees: {employees_data}")

            # Pobranie danych z tabeli services
            query_services = "SELECT service_id, service_type FROM services"
            cursor = self.employee_service_controller.db_controller.connection.execute(query_services)
            services_data = {row["service_id"]: row["service_type"] for row in cursor.fetchall()}
            # print(f"[### EMPLOYEE_SERVICE] Dane z tabeli services: {services_data}")

            # Formatowanie danych
            formatted_data = []
            for record in employee_services_data:
                employee_id = record.get("employee_id")
                service_id = record.get("service_id")

                # Pobranie danych pracownika
                first_name = employees_data.get(employee_id, {}).get("first_name", "Nieznany")
                last_name = employees_data.get(employee_id, {}).get("last_name", "Nieznany")

                # Pobranie typu usługi
                service_type = services_data.get(service_id, "Nieznany")

                # Dodanie danych do rekordu
                formatted_record = {
                    **record,  # Dane z employee_services
                    "first_name": first_name,
                    "last_name": last_name,
                    "service_type": service_type,
                }
                formatted_data.append(formatted_record)

            # print(f"[### EMPLOYEE_SERVICE] Sformatowane dane: {formatted_data}")
            return formatted_data
        except KeyError as ke:
            print(f"[### EMPLOYEE_SERVICE] Brak klucza w danych: {str(ke)}")
            return []
        except AttributeError as ae:
            print(f"[### EMPLOYEE_SERVICE] Błąd atrybutu: {str(ae)}")
            return []


    def get_formatted_employee_specialties(self):
        """
        Pobiera dane z tabeli employee_specialties, employees i specialties.
        Formatuje dane tak, aby zawierały szczegóły pracownika i specjalizacji.

        Returns:
            list[dict]: Lista sformatowanych rekordów.
        """
        try:
            # Pobranie wszystkich rekordów z tabeli employee_specialties
            query_employee_specialties = "SELECT * FROM employee_specialties"
            cursor = self.employee_service_controller.db_controller.connection.execute(query_employee_specialties)
            employee_specialties_data = [dict(row) for row in cursor.fetchall()]
            # print(f"[### EMPLOYEE_SERVICE] Pobranie danych z tabeli employee_specialties: {employee_specialties_data}")

            # Pobranie kolumn employee_id, first_name, last_name z tabeli employees
            query_employees = "SELECT employee_id, first_name, last_name FROM employees"
            cursor = self.employee_service_controller.db_controller.connection.execute(query_employees)
            employees_data = {row["employee_id"]: {"first_name": row["first_name"], "last_name": row["last_name"]}
                              for row in cursor.fetchall()}
            # print(f"[### EMPLOYEE_SERVICE] Pobranie danych z tabeli employees: {employees_data}")

            # Pobranie kolumn specialty_id, specialty_name z tabeli specialties
            query_specialties = "SELECT specialty_id, specialty_name FROM specialties"
            cursor = self.employee_service_controller.db_controller.connection.execute(query_specialties)
            specialties_data = {row["specialty_id"]: {"specialty_name": row["specialty_name"]}
                                for row in cursor.fetchall()}
            # print(f"[### EMPLOYEE_SERVICE] Pobranie danych z tabeli specialties: {specialties_data}")

            # Formatowanie danych
            formatted_data = []
            for specialty in employee_specialties_data:
                employee_id = specialty.get("employee_id")
                specialty_id = specialty.get("specialty_id")

                formatted_record = {
                    **specialty,  # Wszystkie kolumny z tabeli employee_specialties
                    "first_name": employees_data.get(employee_id, {}).get("first_name", "Brak danych"),
                    "last_name": employees_data.get(employee_id, {}).get("last_name", "Brak danych"),
                    "specialty_name": specialties_data.get(specialty_id, {}).get("specialty_name", "Brak danych")
                }
                formatted_data.append(formatted_record)

            # print(f"[### EMPLOYEE_SERVICE] Sformatowane dane: {formatted_data}")
            return formatted_data
        except KeyError as key_error:
            print(f"[### EMPLOYEE_SERVICE] Błąd klucza: {str(key_error)}")
            raise
        except AttributeError as ae:
            print(f"[### EMPLOYEE_SERVICE] Błąd atrybutu: {str(ae)}")
            return []


    def get_all_employee_specialties(self):
        """
        Pobiera wszystkie rekordy z tabeli `employee_specialties`.

        Returns:
            list[dict]: Lista rekordów w formacie słowników.
        """
        try:
            self.employee_service_controller.db_controller.ensure_connection()
            query = "SELECT * FROM employee_specialties"
            cursor = self.employee_service_controller.db_controller.connection.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except sqlite3.OperationalError as op_err:
            print(f"[get_all_employee_specialties] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[get_all_employee_specialties] Błąd bazy danych: {db_err}")
            return []


    def get_all_employee_services(self):
        """
        Pobiera wszystkie rekordy z tabeli `employee_services`.

        Returns:
            list[dict]: Lista rekordów w formacie słowników.
        """
        try:
            self.employee_service_controller.db_controller.ensure_connection()
            query = "SELECT * FROM employee_services"
            cursor = self.employee_service_controller.db_controller.connection.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except sqlite3.OperationalError as op_err:
            print(f"[get_all_employee_services] Błąd operacyjny bazy danych: {op_err}")
            return []
        except sqlite3.DatabaseError as db_err:
            print(f"[get_all_employee_services] Błąd bazy danych: {db_err}")
            return []
