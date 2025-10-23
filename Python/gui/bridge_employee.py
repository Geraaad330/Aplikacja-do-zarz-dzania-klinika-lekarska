from PySide6.QtCore import QObject, Signal, Slot # pylint: disable=E0611
from services.employee_service import EmployeeService
from controllers.employees_controller import EmployeesController
from controllers.users_accounts_controller import UsersAccountsController
from controllers.assigned_patients_controller import AssignedPatientsController
from controllers.services_controller import ServicesController
from controllers.employee_services_controller import EmployeeServicesController
from controllers.specialties_controller import SpecialtiesController
from controllers.employee_specialties_controller import EmployeeSpecialtiesController

class BridgeEmployee(QObject):
    employeeListChanged = Signal(list)
    servicesListChanged = Signal(list)  # Sygnał dla danych z tabeli services
    specialtiesListChanged = Signal(list)  # Sygnał dla danych z tabeli specialties
    formattedEmployeeServicesChanged = Signal(list)
    employeeSpecialtiesListChanged = Signal(list)  # Sygnał do QML
    employeeAddedSuccessfully = Signal()
    employeeAdditionFailed = Signal(str)
    employeeErrorOccurred = Signal(str)  # NOWY SYGNAŁ
    employeeUpdatedSuccessfully = Signal()
    employeeUpdateFailed = Signal(str)
    employeeDeletedSuccessfully = Signal()
    employeeDeletionFailed = Signal(str)
    serviceAdditionFailed = Signal(str)
    serviceAddedSuccessfully = Signal()
    serviceUpdatedSuccessfully = Signal()
    serviceUpdateFailed = Signal(str)
    serviceDeletedSuccessfully = Signal()
    serviceDeletionFailed = Signal(str)
    specialtyAdditionFailed = Signal(str)
    specialtyAddedSuccessfully = Signal()
    specialtyUpdatedSuccessfully = Signal()
    specialtyUpdateFailed = Signal(str)
    specialtyDeletionFailed = Signal(str)
    specialtyDeletedSuccessfully = Signal()
    employeeServiceAddedSuccessfully = Signal()
    employeeServiceAdditionFailed = Signal(str)
    employeeSpecialtyAddedSuccessfully = Signal()
    employeeSpecialtyAdditionFailed = Signal(str)
    employeeServiceUpdateFailed = Signal(str)
    employeeServiceUpdatedSuccessfully = Signal()
    employeeSpecialtyUpdatedSuccessfully = Signal()
    employeeSpecialtyUpdateFailed = Signal(str)
    employeeSpecialtyDeletedSuccessfully = Signal()
    employeeSpecialtyDeletionFailed = Signal(str)
    employeeServiceDeletionFailed = Signal(str)
    employeeServiceDeletedSuccessfully = Signal()

    def __init__(self, main_controller, parent=None):
        try:
            super().__init__(parent)
            print("bridgeEmployee initialized")  # Debugging
            self.main_controller = main_controller
            self._logged_in_user_id = None
            self._employee_list = []
            self._services_data = []
            self._specialties_data = []
            self._formatted_employee_services = []
            self._employee_specialties_data = []            
        except AttributeError as e:
            print(f"Błąd w __init__: {str(e)} - problem z atrybutami")
        except TypeError as e:
            print(f"Błąd w __init__: {str(e)} - problem z typami danych")

 # -------------------------------------------------------------------------

    @Slot(int)
    def setLoggedInUserId(self, user_id):
        """
        Ustawia ID zalogowanego użytkownika.
        """
        print(f"[BridgeEmployee] Ustawianie zalogowanego użytkownika: {user_id}")
        self._logged_in_user_id = user_id

 # -------------------------------------------------------------------------

    @Slot()
    def updateEmployeeList(self):
        """
        Pobiera listę pracowników przypisanych do aktualnego użytkownika
        i emituje sygnał do QML.
        """
        if self._logged_in_user_id is None:
            print("[BridgeEmployee_updateEmployeeList] Brak zalogowanego użytkownika. Nie można pobrać listy pracowników.")
            self.employeeListChanged.emit([])  # Emituj pustą listę, aby frontend mógł zareagować
            return

        try:
            # Pobranie danych z serwisu pracowników
            employee_controller = EmployeesController(self.main_controller.db_controller)
            employee_list = employee_controller.get_all_employees()

            # Debugowanie pobranych danych
            # print(f"[BridgeEmployee_updateEmployeeList] Pobranie danych pracowników: {employee_list}")
                
            # Aktualizacja listy pracowników
            self._employee_list = employee_list
            
            # Emitowanie sygnału z listą pracowników
            self.employeeListChanged.emit(self._employee_list)

        except KeyError as ke:
            print(f"[BridgeEmployee_updateEmployeeList] Klucz nie znaleziony w danych pracownika: {ke}")
            self.employeeListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except ValueError as ve:
            print(f"[BridgeEmployee_updateEmployeeList] Błąd w wartościach danych pracownika: {ve}")
            self.employeeListChanged.emit([])  # Emituj pustą listę w przypadku błędu

    @Slot(result=list)
    def getEmployeeList(self):
        """
        Zwraca listę pacjentów.
        """
        return self._employee_list

 # -------------------------------------------------------------------------


    

    @Slot()
    def fetchServicesAndSpecialties(self):
        """
        Pobiera dane z tabel services i specialties oraz emituje sygnały do QML.
        """

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_updateEmployeeList] Brak zalogowanego użytkownika. Nie można pobrać listy pracowników.")
            self.employeeListChanged.emit([])  # Emituj pustą listę, aby frontend mógł zareagować
            return

        try:
            # Inicjalizacja EmployeeService
            employee_service = EmployeeService(self.main_controller)
        
            # Wywołanie metody z EmployeeService
            data = employee_service.get_services_and_specialties_table()

            # Pobranie danych z tabeli services i specialties
            services_data = data.get("services", [])
            specialties_data = data.get("specialties", [])

            self._services_data = services_data
            self._specialties_data = specialties_data

            # Debugowanie pobranych danych
            # print(f"[BridgeEmployee_fetchServicesAndSpecialties] Services: {services_data}")
            # print(f"[BridgeEmployee_fetchServicesAndSpecialties] Specialties: {specialties_data}")

            # Emitowanie sygnałów do frontendu
            self.servicesListChanged.emit(services_data)
            self.specialtiesListChanged.emit(specialties_data)

        except AttributeError as ae:
            print(f"[BridgeEmployee_fetchServicesAndSpecialties] Błąd atrybutu: {str(ae)}")
        except KeyError as ke:
            print(f"[BridgeEmployee_fetchServicesAndSpecialties] Brak klucza w danych: {str(ke)}")
        except ValueError as ve:
            print(f"[BridgeEmployee_fetchServicesAndSpecialties] Błąd wartości: {str(ve)}")


    @Slot(result=list)
    def getfetchServicesAndSpecialties(self):
        """
        Zwraca listę pacjentów.
        """
        return  self._services_data, self._specialties_data

 # -------------------------------------------------------------------------


    @Slot()
    def fetchFormattedEmployeeServices(self):
        """
        Wywołuje metodę `get_formatted_employee_services` z `employee_services.py`
        i emituje sygnał z sformatowanymi danymi do QML.
        """
        try:
            # Inicjalizacja EmployeeService
            employee_service = EmployeeService(self.main_controller)

            # Pobranie sformatowanych danych
            formatted_data = employee_service.get_formatted_employee_services()

            # Debugowanie pobranych danych
            # print(f"[BridgeEmployee_fetchFormattedEmployeeServices] Sformatowane dane: {formatted_data}")

            # Przechowywanie i emitowanie danych
            self._formatted_employee_services = formatted_data
            self.formattedEmployeeServicesChanged.emit(formatted_data)

        except KeyError as ke:
            print(f"[BridgeEmployee_fetchFormattedEmployeeServices] Brak klucza w danych: {str(ke)}")
        except ValueError as ve:
            print(f"[BridgeEmployee_fetchFormattedEmployeeServices] Błąd wartości: {str(ve)}")
        except AttributeError as ae:
            print(f"[BridgeEmployee_fetchFormattedEmployeeServices] Błąd atrybutu: {str(ae)}")

    @Slot(result=list)
    def getFormattedEmployeeServices(self):
        """
        Zwraca sformatowaną listę powiązań pracowników i usług.
        """
        return self._formatted_employee_services
    

 # -------------------------------------------------------------------------


    @Slot()
    def fetchEmployeeSpecialties(self):
        """
        Pobiera dane z tabeli employee_specialties i emituje sygnał do QML.
        """

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_fetchEmployeeSpecialties] Brak zalogowanego użytkownika. Nie można pobrać danych.")
            self.employeeSpecialtiesListChanged.emit([])  # Emitowanie pustej listy do QML
            return

        try:
            # Inicjalizacja EmployeeService
            employee_service = EmployeeService(self.main_controller)

            # Pobranie sformatowanych danych pracowników i ich specjalizacji
            formatted_specialties_data = employee_service.get_formatted_employee_specialties()

            # Przechowywanie danych w obiekcie klasy
            self._employee_specialties_data = formatted_specialties_data

            # Debugowanie pobranych danych
            # print(f"[BridgeEmployee_fetchEmployeeSpecialties] Pobrane dane: {formatted_specialties_data}")

            # Emitowanie sygnału do QML
            self.employeeSpecialtiesListChanged.emit(formatted_specialties_data)

        except AttributeError as ae:
            print(f"[BridgeEmployee_fetchEmployeeSpecialties] Błąd atrybutu: {str(ae)}")
        except KeyError as ke:
            print(f"[BridgeEmployee_fetchEmployeeSpecialties] Brak klucza w danych: {str(ke)}")
        except ValueError as ve:
            print(f"[BridgeEmployee_fetchEmployeeSpecialties] Błąd wartości: {str(ve)}")
        
    @Slot(result=list)
    def getEmployeeSpecialties(self):
        """
        Zwraca pobraną listę specjalizacji pracowników.
        """
        return self._employee_specialties_data

 # -------------------------------------------------------------------------

    @Slot(str)
    def checkEmployeeCrudAccess(self, view_name):
        """
        Sprawdza, czy zalogowany użytkownik ma dostęp do danego widoku (EmployeeCRUD, EmployeeServSpecCRUD, EmployeeAssignServSpecCRUD).
        Jeśli nie, emituje sygnał o błędzie.
        """
        if self._logged_in_user_id is None:
            print("[BridgeEmployee_checkEmployeeCrudAccess] Brak zalogowanego użytkownika.")
            self.employeeErrorOccurred.emit("Brak zalogowanego użytkownika.")
            return

        try:
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
            role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)
            print(f"DEBUG: Pobranie role_id dla użytkownika {self._logged_in_user_id} -> role_id: {role_id}")


            # Zestaw ról blokujących dostęp do widoków
            blocked_roles = [3, 4, 5, 6, 7, 8, 11]

            # Mapa widoków do komunikatów błędów
            view_messages = {
                "EmployeeCRUD": "Brak uprawnień do zarządzania pracownikami.",
                "EmployeeServSpecCRUD": "Brak uprawnień do zarządzania usługami i specjalnościami.",
                "EmployeeAssignServSpecCRUD": "Brak uprawnień do zarządzania przypisaniami."
            }

            # Sprawdzenie dostępu
            if role_id in blocked_roles:
                error_message = view_messages.get(view_name, "Brak uprawnień do tego widoku.")
                print(f"[BridgeEmployee_checkEmployeeCrudAccess] {error_message}")
                self.employeeErrorOccurred.emit(error_message)
                return  # Zatrzymujemy dalsze wykonywanie kodu

            print(f"[BridgeEmployee_checkEmployeeCrudAccess] Użytkownik ma dostęp do {view_name}.")

        except AttributeError as ae:
            print(f"[BridgeEmployee_checkEmployeeCrudAccess] Błąd atrybutu: {str(ae)}")
            self.employeeErrorOccurred.emit("Błąd dostępu do danych użytkownika.")
        except KeyError as ke:
            print(f"[BridgeEmployee_checkEmployeeCrudAccess] Błąd klucza: {str(ke)}")
            self.employeeErrorOccurred.emit("Błąd w strukturze danych użytkownika.")
        except TypeError as te:
            print(f"[BridgeEmployee_checkEmployeeCrudAccess] Błąd typu danych: {str(te)}")
            self.employeeErrorOccurred.emit("Błąd przetwarzania danych użytkownika.")


 # -------------------------------------------------------------------------

    @Slot(str, str, str, str, str, str)  # Zmiana ostatniego parametru na str, ponieważ dane przychodzą z QML
    def addNewEmployee(self, first_name, last_name, email, phone, profession, insert_is_medical_staff):
        """
        Dodaje nowego pracownika na podstawie danych z QML.
        """
        print(f"[BridgeEmployee_addNewEmployee] Odebrano dane pracownika: {first_name}, {last_name}, {email}, {phone}, {profession}, {insert_is_medical_staff}")

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_addNewEmployee] Brak zalogowanego użytkownika.")
            self.employeeAdditionFailed.emit("Brak zalogowanego użytkownika.")
            return

        # Normalizacja wartości is_medical_staff
        normalized_is_medical_staff = insert_is_medical_staff.strip().lower()
        if normalized_is_medical_staff == "tak":
            is_medical_staff = 1
        elif normalized_is_medical_staff == "nie":
            is_medical_staff = 0
        else:
            self.employeeAdditionFailed.emit("Niepoprawna wartość dla pola 'Personel medyczny'. Użyj 'Tak' lub 'Nie'.")
            return

        try:
            employees_controller = EmployeesController(self.main_controller.db_controller)

            # Walidacja unikalnych wartości email i telefonu
            existing_data = employees_controller.get_all_emails_and_phones()
            existing_phones = {str(item["phone"]) for item in existing_data}
            existing_emails = {item["email"] for item in existing_data}

            errors = []

            if phone in existing_phones:
                errors.append(f"Numer telefonu ({phone}) już istnieje w bazie.")
            if email in existing_emails:
                errors.append(f"Adres email ({email}) już istnieje w bazie.")

            # Sprawdzenie poprawności zawodu
            existing_professions = employees_controller.get_all_professions()
            if profession not in existing_professions:
                errors.append(f"Podany zawód ({profession}) nie znajduje się w bazie.")
                errors.append(f"Dostępne zawody: {existing_professions}")

            # Jeśli są błędy, emitujemy błąd
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeEmployee_addNewEmployee] Błędy walidacji: {error_message}")
                self.employeeAdditionFailed.emit(error_message)
                return

            # Przekazanie dodania pracownika do modelu
            result = employees_controller.add_new_employee(
                first_name, last_name, email, phone, profession, is_medical_staff, is_active=1
            )

            # Sprawdzenie, czy operacja zakończyła się sukcesem
            if result["success"]:
                print("[BridgeEmployee_addNewEmployee] Pracownik dodany pomyślnie!")
                self.employeeAddedSuccessfully.emit()
            else:
                print(f"[BridgeEmployee_addNewEmployee] Błąd dodawania: {result['message']}")
                self.employeeAdditionFailed.emit(result["message"])

        except ValueError as ve:
            print(f"[BridgeEmployee_addNewEmployee] Błąd wartości: {str(ve)}")
            self.employeeAdditionFailed.emit(str(ve))
        except KeyError as ke:
            print(f"[BridgeEmployee_addNewEmployee] Błąd klucza w danych: {str(ke)}")
            self.employeeAdditionFailed.emit("Błąd w strukturze danych.")

 # -------------------------------------------------------------------------




    @Slot(str, str, str, str, str, str, str, str)
    def updateEmployee(self, insert_employee_id, first_name, last_name, email, phone, profession, insert_is_medical_staff, insert_is_active):
        """
        Aktualizuje dane pracownika na podstawie ID.
        """
        print(f"[BridgeEmployee_updateEmployee] Odebrano dane do aktualizacji: {insert_employee_id}, {first_name}, {last_name}, {email}, {phone}, {profession}, {insert_is_medical_staff}, {insert_is_active}")

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_updateEmployee] Brak zalogowanego użytkownika.")
            self.employeeUpdateFailed.emit("Brak zalogowanego użytkownika.")
            return

        # Konwersja ID na int, zakładając, że ID są liczbami
        try:
            employee_id = int(insert_employee_id)
        except ValueError:
            self.employeeUpdateFailed.emit("ID pracownika musi być liczbą.")
            return

        try:
            employees_controller = EmployeesController(self.main_controller.db_controller)

            # Pobranie wszystkich employee_id z bazy
            all_employee_ids = employees_controller.get_all_employee_ids()
            if employee_id not in all_employee_ids:
                msg = f"Pracownik o ID ({employee_id}) nie istnieje w bazie."
                print("[BridgeEmployee_updateEmployee] " + msg)
                self.employeeUpdateFailed.emit(msg)
                return

            # Pobranie szczegółowych danych pracownika
            employee_data = employees_controller.get_employee(employee_id)
            if not employee_data:
                msg = f"Błąd podczas pobierania szczegółów pracownika o ID ({employee_id})."
                print("[BridgeEmployee_updateEmployee] " + msg)
                self.employeeUpdateFailed.emit(msg)
                return

            # Lista do przechowywania błędów
            errors = []

            # Sprawdzenie unikalności danych – numer telefonu porównujemy jako ciąg znaków
            existing_data = employees_controller.get_all_emails_and_phones()
            existing_phones = {str(emp["phone"]) for emp in existing_data}
            existing_emails = {emp["email"] for emp in existing_data}

            if phone and phone != str(employee_data["phone"]) and phone in existing_phones:
                errors.append(f"Numer telefonu ({phone}) już istnieje w bazie.")
            if email and email != employee_data["email"] and email in existing_emails:
                errors.append(f"Adres email ({email}) już istnieje w bazie.")

            # Sprawdzenie poprawności zawodu – walidacja, jeżeli użytkownik podał wartość
            existing_professions = employees_controller.get_all_professions()
            if profession and profession not in existing_professions:
                errors.append(f"Podany zawód ({profession}) nie znajduje się w bazie.")
                errors.append(f"Dostępne zawody: {existing_professions}")

            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeEmployee_updateEmployee] Błędy walidacji: {error_message}")
                self.employeeUpdateFailed.emit(error_message)
                return

            # Normalizacja wartości is_medical_staff (pole opcjonalne)
            is_medical_staff = None
            if insert_is_medical_staff:
                normalized_is_medical_staff = insert_is_medical_staff.strip().lower()
                if normalized_is_medical_staff == "tak":
                    is_medical_staff = 1
                elif normalized_is_medical_staff == "nie":
                    is_medical_staff = 0
                else:
                    self.employeeUpdateFailed.emit("Niepoprawna wartość dla pola 'Personel medyczny'. Użyj 'Tak' lub 'Nie'.")
                    return

            # Normalizacja wartości is_active (pole opcjonalne)
            is_active = None
            if insert_is_active:
                normalized_is_active = insert_is_active.strip().lower()
                if normalized_is_active == "tak":
                    is_active = 1
                elif normalized_is_active == "nie":
                    is_active = 0
                else:
                    self.employeeUpdateFailed.emit("Niepoprawna wartość dla pola 'Aktywność'. Użyj 'Tak' lub 'Nie'.")
                    return

            # Budowanie słownika danych do aktualizacji – tylko dla pól, które uległy zmianie
            data_to_update = {}
            if first_name and first_name != employee_data["first_name"]:
                data_to_update["first_name"] = first_name
            if last_name and last_name != employee_data["last_name"]:
                data_to_update["last_name"] = last_name
            if email and email != employee_data["email"]:
                data_to_update["email"] = email
            if phone and phone != str(employee_data["phone"]):
                data_to_update["phone"] = phone
            if profession and profession != employee_data["profession"]:
                data_to_update["profession"] = profession
            if is_medical_staff is not None and is_medical_staff != employee_data.get("is_medical_staff"):
                data_to_update["is_medical_staff"] = is_medical_staff
            if is_active is not None and is_active != employee_data.get("is_active"):
                data_to_update["is_active"] = is_active 


            if not data_to_update:
                print("[BridgeEmployee_updateEmployee] Brak zmian w danych pracownika. Aktualizacja nie została wykonana.")
                self.employeeUpdateFailed.emit("Brak zmian w danych pracownika.")
                return

            # Wywołanie aktualizacji w kontrolerze
            employees_controller.update_employee(employee_id, **data_to_update)
            print("[BridgeEmployee_updateEmployee] Pracownik został zaktualizowany w bazie danych.")
            self.employeeUpdatedSuccessfully.emit()

        except ValueError as ve:
            print(f"[BridgeEmployee_updateEmployee] Błąd wartości: {str(ve)}")
            self.employeeUpdateFailed.emit(str(ve))
        except KeyError as ke:
            print(f"[BridgeEmployee_updateEmployee] Błąd klucza w danych: {str(ke)}")
            self.employeeUpdateFailed.emit("Błąd w strukturze danych.")



 # -------------------------------------------------------------------------

    @Slot(int)
    def deleteEmployee(self, insert_employee_id):
        """
        Usuwa pracownika na podstawie podanego employee_id, o ile nie jest on przypisany do pacjentów.
        """
        print(f"[BridgeEmployee_deleteEmployee] Otrzymano żądanie usunięcia pracownika o ID: {insert_employee_id}")

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_deleteEmployee] Brak zalogowanego użytkownika.")
            self.employeeDeletionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            employees_controller = EmployeesController(self.main_controller.db_controller)

            # Pobranie wszystkich `employee_id` z bazy danych
            all_employee_ids = employees_controller.get_all_employee_ids()

            # Sprawdzenie, czy podany `insert_employee_id` istnieje w bazie
            if insert_employee_id not in all_employee_ids:
                msg = f"Pracownik o ID ({insert_employee_id}) nie istnieje w bazie."
                print(f"[BridgeEmployee_deleteEmployee] {msg}")
                self.employeeDeletionFailed.emit(msg)
                return

            # Pobranie przypisań pacjentów do pracowników
            assigned_patients_controller = AssignedPatientsController(self.main_controller.db_controller)
            assigned_patients = assigned_patients_controller.get_all_assigned_patients()

            # Sprawdzenie, czy pracownik jest przypisany w `assigned_patients`
            assigned_assignments = [
                record["assignment_id"] for record in assigned_patients if record["fk_employee_id"] == insert_employee_id
            ]

            if assigned_assignments:
                msg = (f"Nie można usunąć pracownika o ID ({insert_employee_id}), "
                    f"ponieważ jest przypisany w następujących assignment_id: {', '.join(map(str, assigned_assignments))}.")
                print(f"[BridgeEmployee_deleteEmployee] {msg}")
                self.employeeDeletionFailed.emit(msg)
                return

            # Usunięcie pracownika
            employees_controller.delete_employee(insert_employee_id)

            print(f"[BridgeEmployee_deleteEmployee] Pracownik o ID {insert_employee_id} został usunięty.")
            self.employeeDeletedSuccessfully.emit()

        except ValueError as ve:
            print(f"[BridgeEmployee_deleteEmployee] Błąd wartości: {str(ve)}")
            self.employeeDeletionFailed.emit(str(ve))

        except RuntimeError as re:
            print(f"[BridgeEmployee_deleteEmployee] Błąd bazy danych: {str(re)}")
            self.employeeDeletionFailed.emit("Błąd systemu podczas usuwania pracownika.")

        except KeyError as ke:
            print(f"[BridgeEmployee_deleteEmployee] Błąd klucza w danych: {str(ke)}")
            self.employeeDeletionFailed.emit("Błąd w strukturze danych.")

 # -------------------------------------------------------------------------

    @Slot(str, int, float)  # Wszystkie dane przychodzą jako stringi z QML
    def addNewService(self, service_type, duration_minutes, service_price):
        """
        Dodaje nową usługę na podstawie danych z QML.
        """
        print(f"[BridgeEmployee_addNewService] Odebrano dane usługi: {service_type}, {duration_minutes}, {service_price}")

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_addNewService] Brak zalogowanego użytkownika.")
            self.serviceAdditionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            services_controller = ServicesController(self.main_controller.db_controller)

            # Pobranie wszystkich istniejących typów usług
            existing_service_types = services_controller.get_all_service_types()

            # Konwersja listy na małe litery dla porównania (ignorowanie wielkości liter)
            existing_service_types_lower = {service.lower() for service in existing_service_types}

            # Konwersja wpisanego service_type na małe litery
            service_type_lower = service_type.lower()

            # Sprawdzenie, czy podany service_type już istnieje (bez uwzględniania wielkości liter)
            if service_type_lower in existing_service_types_lower:
                error_message = f"Usługa '{service_type}' już istnieje w bazie."
                print(f"[BridgeEmployee_addNewService] {error_message}")
                self.serviceAdditionFailed.emit(error_message)
                return

            # Dodanie usługi do bazy
            result = services_controller.add_service(
                service_type, duration_minutes, service_price, is_active=1  # is_active zawsze 1
            )

            # Sprawdzenie wyniku operacji
            if result["success"]:
                print("[BridgeEmployee_addNewService] Usługa dodana pomyślnie!")
                self.serviceAddedSuccessfully.emit()
            else:
                print(f"[BridgeEmployee_addNewService] Błąd dodawania: {result['message']}")
                self.serviceAdditionFailed.emit(result["message"])

        except ValueError as ve:
            print(f"[BridgeEmployee_addNewService] Błąd wartości: {str(ve)}")
            self.serviceAdditionFailed.emit(str(ve))
        except KeyError as ke:
            print(f"[BridgeEmployee_addNewService] Błąd klucza w danych: {str(ke)}")
            self.serviceAdditionFailed.emit("Błąd w strukturze danych.")
        except RuntimeError as re:
            print(f"[BridgeEmployee_addNewService] Błąd bazy danych: {str(re)}")
            self.serviceAdditionFailed.emit("Wystąpił błąd bazy danych.")

 # -------------------------------------------------------------------------

    @Slot(str, str, str, str, str)  # Wszystkie dane przychodzą jako stringi z QML
    def updateService(self, insert_service_id, service_type, duration_minutes, service_price, insert_is_active):
        """
        Aktualizuje dane usługi na podstawie ID.
        """
        print(f"[BridgeEmployee_updateService] Odebrano dane do aktualizacji: {insert_service_id}, {service_type}, {duration_minutes}, {service_price}, {insert_is_active}")

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_updateService] Brak zalogowanego użytkownika.")
            self.serviceUpdateFailed.emit("Brak zalogowanego użytkownika.")
            return

        # Konwersja ID na int, zakładając, że ID są liczbami
        try:
            service_id = int(insert_service_id)
        except ValueError:
            self.serviceUpdateFailed.emit("ID usługi musi być liczbą całkowitą.")
            return

        try:
            services_controller = ServicesController(self.main_controller.db_controller)

            # Pobranie wszystkich service_id z bazy
            all_service_ids = services_controller.get_all_service_ids()
            if service_id not in all_service_ids:
                msg = f"Usługa o ID ({service_id}) nie istnieje w bazie."
                print("[BridgeEmployee_updateService] " + msg)
                self.serviceUpdateFailed.emit(msg)
                return

            # Pobranie wszystkich typów usług
            existing_service_types = services_controller.get_all_service_types()
            normalized_service_type = service_type.strip().lower()

            # Sprawdzenie, czy podany service_type już istnieje (bez uwzględniania wielkości liter)
            if any(existing_type.lower() == normalized_service_type for existing_type in existing_service_types):
                error_message = f"Usługa '{service_type}' już istnieje w bazie."
                print(f"[BridgeEmployee_updateService] {error_message}")
                self.serviceUpdateFailed.emit(error_message)
                return

            # Normalizacja wartości is_active (pole opcjonalne)
            is_active = None
            if insert_is_active:
                normalized_is_active = insert_is_active.strip().lower()
                if normalized_is_active == "tak":
                    is_active = 1
                elif normalized_is_active == "nie":
                    is_active = 0
                else:
                    self.serviceUpdateFailed.emit("Niepoprawna wartość dla pola 'Aktywność'. Użyj 'Tak' lub 'Nie'.")
                    return

            # Pobranie szczegółowych danych usługi
            service_data = services_controller.get_service_by_id(service_id)
            if not service_data:
                msg = f"Błąd podczas pobierania szczegółów usługi o ID ({service_id})."
                print("[BridgeEmployee_updateService] " + msg)
                self.serviceUpdateFailed.emit(msg)
                return

            # Budowanie słownika danych do aktualizacji – tylko dla pól, które uległy zmianie
            data_to_update = {}
            if service_type and service_type != service_data["service_type"]:
                data_to_update["service_type"] = service_type
            if duration_minutes and int(duration_minutes) != service_data["duration_minutes"]:
                data_to_update["duration_minutes"] = int(duration_minutes)
            if service_price and float(service_price) != service_data["service_price"]:
                data_to_update["service_price"] = float(service_price)
            if is_active is not None and is_active != service_data.get("is_active"):
                data_to_update["is_active"] = is_active

            if not data_to_update:
                print("[BridgeEmployee_updateService] Brak zmian w danych usługi. Aktualizacja nie została wykonana.")
                self.serviceUpdateFailed.emit("Brak zmian w danych usługi.")
                return

            # Wywołanie aktualizacji w kontrolerze
            services_controller.update_service(service_id, data_to_update)
            print("[BridgeEmployee_updateService] Usługa została zaktualizowana w bazie danych.")
            self.serviceUpdatedSuccessfully.emit()

        except ValueError as ve:
            print(f"[BridgeEmployee_updateService] Błąd wartości: {str(ve)}")
            self.serviceUpdateFailed.emit(str(ve))
        except KeyError as ke:
            print(f"[BridgeEmployee_updateService] Błąd klucza w danych: {str(ke)}")
            self.serviceUpdateFailed.emit("Błąd w strukturze danych.")
        except RuntimeError as re:
            print(f"[BridgeEmployee_updateService] Błąd bazy danych: {str(re)}")
            self.serviceUpdateFailed.emit("Wystąpił błąd bazy danych.")


 # -------------------------------------------------------------------------

    @Slot(int)
    def deleteService(self, insert_service_id):
        """
        Usuwa usługę na podstawie podanego service_id, o ile nie jest ona przypisana do pracowników.
        """
        print(f"[BridgeEmployee_deleteService] Otrzymano żądanie usunięcia usługi o ID: {insert_service_id}")

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_deleteService] Brak zalogowanego użytkownika.")
            self.serviceDeletionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            services_controller = ServicesController(self.main_controller.db_controller)
            employee_services_controller = EmployeeServicesController(self.main_controller.db_controller)

            # Pobranie wszystkich `service_id` z bazy
            all_service_ids = services_controller.get_all_service_ids()

            # Sprawdzenie, czy podany `insert_service_id` istnieje w bazie
            if insert_service_id not in all_service_ids:
                msg = f"Usługa o ID ({insert_service_id}) nie istnieje w bazie."
                print(f"[BridgeEmployee_deleteService] {msg}")
                self.serviceDeletionFailed.emit(msg)
                return

            # Pobranie przypisań usług do pracowników
            employee_services = employee_services_controller.get_all_employee_services()

            # Sprawdzenie, czy usługa jest przypisana w `employee_services`
            assigned_services = [
                record["employee_service_id"] for record in employee_services if record["service_id"] == insert_service_id
            ]

            if assigned_services:
                msg = (f"Nie można usunąć usługi o ID ({insert_service_id}), "
                    f"ponieważ jest przypisana w następujących employee_service_id: {', '.join(map(str, assigned_services))}.")
                print(f"[BridgeEmployee_deleteService] {msg}")
                self.serviceDeletionFailed.emit(msg)
                return

            # Usunięcie usługi
            services_controller.delete_service(insert_service_id)

            print(f"[BridgeEmployee_deleteService] Usługa o ID {insert_service_id} została usunięta.")
            self.serviceDeletedSuccessfully.emit()

        except ValueError as ve:
            print(f"[BridgeEmployee_deleteService] Błąd wartości: {str(ve)}")
            self.serviceDeletionFailed.emit(str(ve))

        except RuntimeError as re:
            print(f"[BridgeEmployee_deleteService] Błąd bazy danych: {str(re)}")
            self.serviceDeletionFailed.emit("Błąd systemu podczas usuwania usługi.")

        except KeyError as ke:
            print(f"[BridgeEmployee_deleteService] Błąd klucza w danych: {str(ke)}")
            self.serviceDeletionFailed.emit("Błąd w strukturze danych.")


 # -------------------------------------------------------------------------

    @Slot(str)  # Wszystkie dane przychodzą jako stringi z QML
    def addNewSpecialty(self, insert_specialty_name):
        """
        Dodaje nową specjalność na podstawie danych z QML.
        """
        print(f"[BridgeEmployee_addNewSpecialty] Odebrano dane specjalności: {insert_specialty_name}")

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_addNewSpecialty] Brak zalogowanego użytkownika.")
            self.specialtyAdditionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            specialties_controller = SpecialtiesController(self.main_controller.db_controller)

            # Pobranie wszystkich istniejących specjalności
            existing_specialties = specialties_controller.get_all_specialty_names()

            # Konwersja listy specjalności na małe litery dla porównania (ignorowanie wielkości liter)
            existing_specialties_lower = {specialty.lower() for specialty in existing_specialties}

            # Konwersja wpisanej specjalności na małe litery
            specialty_name_lower = insert_specialty_name.strip().lower()

            # Sprawdzenie, czy podana specjalność już istnieje (bez uwzględniania wielkości liter)
            if specialty_name_lower in existing_specialties_lower:
                error_message = f"Specjalność '{insert_specialty_name}' już istnieje w bazie."
                print(f"[BridgeEmployee_addNewSpecialty] {error_message}")
                self.specialtyAdditionFailed.emit(error_message)
                return

            # Dodanie specjalności do bazy (is_active zawsze = 1)
            result = specialties_controller.add_specialty(insert_specialty_name, is_active=1)

            # Sprawdzenie wyniku operacji
            if result["success"]:
                print("[BridgeEmployee_addNewSpecialty] Specjalność dodana pomyślnie!")
                self.specialtyAddedSuccessfully.emit()
            else:
                print(f"[BridgeEmployee_addNewSpecialty] Błąd dodawania: {result['message']}")
                self.specialtyAdditionFailed.emit(result["message"])

        except ValueError as ve:
            print(f"[BridgeEmployee_addNewSpecialty] Błąd wartości: {str(ve)}")
            self.specialtyAdditionFailed.emit(str(ve))
        except KeyError as ke:
            print(f"[BridgeEmployee_addNewSpecialty] Błąd klucza w danych: {str(ke)}")
            self.specialtyAdditionFailed.emit("Błąd w strukturze danych.")
        except RuntimeError as re:
            print(f"[BridgeEmployee_addNewSpecialty] Błąd bazy danych: {str(re)}")
            self.specialtyAdditionFailed.emit("Wystąpił błąd bazy danych.")

 # -------------------------------------------------------------------------

    @Slot(str, str, str)  # Wszystkie dane przychodzą jako stringi z QML
    def updateSpecialty(self, insert_specialty_id, insert_specialty_name, insert_is_active):
        """
        Aktualizuje dane specjalności na podstawie ID.
        """
        print(f"[BridgeEmployee_updateSpecialty] Odebrano dane do aktualizacji: {insert_specialty_id}, {insert_specialty_name}, {insert_is_active}")

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_updateSpecialty] Brak zalogowanego użytkownika.")
            self.specialtyUpdateFailed.emit("Brak zalogowanego użytkownika.")
            return

        # Konwersja ID na int, zakładając, że ID są liczbą całkowitą
        try:
            specialty_id = int(insert_specialty_id)
        except ValueError:
            self.specialtyUpdateFailed.emit("ID specjalności musi być liczbą całkowitą.")
            return

        try:
            specialties_controller = SpecialtiesController(self.main_controller.db_controller)

            # Pobranie wszystkich specialty_id z bazy
            all_specialty_ids = specialties_controller.get_all_specialty_ids()
            if specialty_id not in all_specialty_ids:
                msg = f"Specjalność o ID ({specialty_id}) nie istnieje w bazie."
                print("[BridgeEmployee_updateSpecialty] " + msg)
                self.specialtyUpdateFailed.emit(msg)
                return

            # Pobranie wszystkich nazw specjalności
            existing_specialty_names = specialties_controller.get_all_specialty_names()
            normalized_specialty_name = insert_specialty_name.strip().lower()

            # Sprawdzenie, czy podana nazwa specjalności już istnieje (bez uwzględniania wielkości liter)
            if any(existing_name.lower() == normalized_specialty_name for existing_name in existing_specialty_names):
                error_message = f"Specjalność '{insert_specialty_name}' już istnieje w bazie."
                print(f"[BridgeEmployee_updateSpecialty] {error_message}")
                self.specialtyUpdateFailed.emit(error_message)
                return

            # Normalizacja wartości is_active (pole opcjonalne)
            is_active = None
            if insert_is_active:
                normalized_is_active = insert_is_active.strip().lower()
                if normalized_is_active == "tak":
                    is_active = 1
                elif normalized_is_active == "nie":
                    is_active = 0
                else:
                    self.specialtyUpdateFailed.emit("Niepoprawna wartość dla pola 'Aktywność'. Użyj 'Tak' lub 'Nie'.")
                    return

            # Pobranie szczegółowych danych specjalności
            specialty_data = specialties_controller.get_specialty_by_id(specialty_id)
            if not specialty_data:
                msg = f"Błąd podczas pobierania szczegółów specjalności o ID ({specialty_id})."
                print("[BridgeEmployee_updateSpecialty] " + msg)
                self.specialtyUpdateFailed.emit(msg)
                return

            # Budowanie słownika danych do aktualizacji – tylko dla pól, które uległy zmianie
            data_to_update = {}
            if insert_specialty_name and insert_specialty_name != specialty_data["specialty_name"]:
                data_to_update["specialty_name"] = insert_specialty_name
            if is_active is not None and is_active != specialty_data.get("is_active"):
                data_to_update["is_active"] = is_active

            if not data_to_update:
                print("[BridgeEmployee_updateSpecialty] Brak zmian w danych specjalności. Aktualizacja nie została wykonana.")
                self.specialtyUpdateFailed.emit("Brak zmian w danych specjalności.")
                return

            # Wywołanie aktualizacji w kontrolerze
            specialties_controller.update_specialty(specialty_id, data_to_update)
            print("[BridgeEmployee_updateSpecialty] Specjalność została zaktualizowana w bazie danych.")
            self.specialtyUpdatedSuccessfully.emit()

        except ValueError as ve:
            print(f"[BridgeEmployee_updateSpecialty] Błąd wartości: {str(ve)}")
            self.specialtyUpdateFailed.emit(str(ve))
        except KeyError as ke:
            print(f"[BridgeEmployee_updateSpecialty] Błąd klucza w danych: {str(ke)}")
            self.specialtyUpdateFailed.emit("Błąd w strukturze danych.")
        except RuntimeError as re:
            print(f"[BridgeEmployee_updateSpecialty] Błąd bazy danych: {str(re)}")
            self.specialtyUpdateFailed.emit("Wystąpił błąd bazy danych.")

 # -------------------------------------------------------------------------

    @Slot(int)
    def deleteSpecialty(self, insert_specialty_id):
        """
        Usuwa specjalność na podstawie podanego specialty_id, o ile nie jest ona przypisana do pracowników.
        """
        print(f"[BridgeEmployee_deleteSpecialty] Otrzymano żądanie usunięcia specjalności o ID: {insert_specialty_id}")

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_deleteSpecialty] Brak zalogowanego użytkownika.")
            self.specialtyDeletionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            specialties_controller = SpecialtiesController(self.main_controller.db_controller)
            employee_specialties_controller = EmployeeSpecialtiesController(self.main_controller.db_controller)

            # Pobranie wszystkich `specialty_id` z bazy
            all_specialty_ids = specialties_controller.get_all_specialty_ids()

            # Sprawdzenie, czy podany `insert_specialty_id` istnieje w bazie
            if insert_specialty_id not in all_specialty_ids:
                msg = f"Specjalność o ID ({insert_specialty_id}) nie istnieje w bazie."
                print(f"[BridgeEmployee_deleteSpecialty] {msg}")
                self.specialtyDeletionFailed.emit(msg)
                return

            # Pobranie przypisań specjalności do pracowników
            employee_specialties = employee_specialties_controller.get_all_employee_specialties()

            # Sprawdzenie, czy specjalność jest przypisana w `employee_specialties`
            assigned_specialties = [
                record["employee_specialty_id"] for record in employee_specialties if record["specialty_id"] == insert_specialty_id
            ]

            if assigned_specialties:
                msg = (f"Nie można usunąć specjalności o ID ({insert_specialty_id}), "
                    f"ponieważ jest przypisana w następujących employee_specialty_id: {', '.join(map(str, assigned_specialties))}.")
                print(f"[BridgeEmployee_deleteSpecialty] {msg}")
                self.specialtyDeletionFailed.emit(msg)
                return

            # Usunięcie specjalności
            specialties_controller.delete_specialty(insert_specialty_id)

            print(f"[BridgeEmployee_deleteSpecialty] Specjalność o ID {insert_specialty_id} została usunięta.")
            self.specialtyDeletedSuccessfully.emit()

        except ValueError as ve:
            print(f"[BridgeEmployee_deleteSpecialty] Błąd wartości: {str(ve)}")
            self.specialtyDeletionFailed.emit(str(ve))

        except RuntimeError as re:
            print(f"[BridgeEmployee_deleteSpecialty] Błąd bazy danych: {str(re)}")
            self.specialtyDeletionFailed.emit("Błąd systemu podczas usuwania specjalności.")

        except KeyError as ke:
            print(f"[BridgeEmployee_deleteSpecialty] Błąd klucza w danych: {str(ke)}")
            self.specialtyDeletionFailed.emit("Błąd w strukturze danych.")

 # -------------------------------------------------------------------------

    @Slot(str, str)
    def addEmployeeToService(self, insert_employee_id, insert_service_id):
        """
        Dodaje przypisanie pracownika do usługi na podstawie danych z QML.
        """
        print(f"[BridgeEmployee_addEmployeeToService] Odebrano dane przypisania: EmployeeID={insert_employee_id}, ServiceID={insert_service_id}")

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_addEmployeeToService] Brak zalogowanego użytkownika.")
            self.employeeServiceAdditionFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []  # Lista do zbierania błędów

        # Konwersja ID na int, zakładając, że ID są liczbami
        try:
            employee_id = int(insert_employee_id)
            service_id = int(insert_service_id)
        except ValueError:
            errors.append("ID pracownika i ID usługi muszą być liczbami całkowitymi.")

        try:
            employee_services_controller = EmployeeServicesController(self.main_controller.db_controller)
            services_controller = ServicesController(self.main_controller.db_controller)
            employees_controller = EmployeesController(self.main_controller.db_controller)

            # Pobranie wszystkich employee_id i service_id z bazy
            all_employee_ids = employees_controller.get_all_employee_ids()
            all_service_ids = services_controller.get_all_service_ids()

            # Sprawdzenie, czy podane ID istnieją w bazie
            if employee_id not in all_employee_ids:
                errors.append(f"Pracownik o ID ({employee_id}) nie istnieje w bazie.")

            if service_id not in all_service_ids:
                errors.append(f"Usługa o ID ({service_id}) nie istnieje w bazie.")

            # Jeśli są błędy na tym etapie, emitujemy je i przerywamy działanie
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeEmployee_addEmployeeToService] Błędy walidacji:\n{error_message}")
                self.employeeServiceAdditionFailed.emit(error_message)
                return

            # Pobranie wszystkich przypisań employee_service
            existing_employee_services = employee_services_controller.get_all_employee_services()

            # Sprawdzenie, czy podane przypisanie już istnieje
            if any(record["employee_id"] == employee_id and record["service_id"] == service_id for record in existing_employee_services):
                errors.append(f"Pracownik o ID ({employee_id}) jest już przypisany do usługi o ID ({service_id}).")

            # Jeśli są błędy w przypisaniach, emitujemy je i przerywamy działanie
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeEmployee_addEmployeeToService] Błędy walidacji:\n{error_message}")
                self.employeeServiceAdditionFailed.emit(error_message)
                return

            # Dodanie przypisania do bazy (is_active zawsze = 1)
            employee_services_controller.add_employee_service_by_ids(employee_id, service_id, is_active=1)

            print("[BridgeEmployee_addEmployeeToService] Pracownik został przypisany do usługi pomyślnie!")
            self.employeeServiceAddedSuccessfully.emit()

        except ValueError as ve:
            print(f"[BridgeEmployee_addEmployeeToService] Błąd wartości: {str(ve)}")
            self.employeeServiceAdditionFailed.emit(str(ve))

        except KeyError as ke:
            print(f"[BridgeEmployee_addEmployeeToService] Błąd klucza w danych: {str(ke)}")
            self.employeeServiceAdditionFailed.emit("Błąd w strukturze danych.")

        except RuntimeError as re:
            print(f"[BridgeEmployee_addEmployeeToService] Błąd bazy danych: {str(re)}")
            self.employeeServiceAdditionFailed.emit("Wystąpił błąd bazy danych.")

 # -------------------------------------------------------------------------

    @Slot(str, str)
    def addEmployeeToSpecialty(self, insert_employee_id, insert_specialty_id):
        """
        Dodaje przypisanie pracownika do specjalności na podstawie danych z QML.
        """
        print(f"[BridgeEmployee_addEmployeeToSpecialty] Odebrano dane przypisania: EmployeeID={insert_employee_id}, SpecialtyID={insert_specialty_id}")

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_addEmployeeToSpecialty] Brak zalogowanego użytkownika.")
            self.employeeSpecialtyAdditionFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []  # Lista do zbierania błędów

        # Konwersja ID na int, zakładając, że ID są liczbami
        try:
            employee_id = int(insert_employee_id)
            specialty_id = int(insert_specialty_id)
        except ValueError:
            errors.append("ID pracownika i ID specjalności muszą być liczbami całkowitymi.")

        try:
            employee_specialties_controller = EmployeeSpecialtiesController(self.main_controller.db_controller)
            specialties_controller = SpecialtiesController(self.main_controller.db_controller)
            employees_controller = EmployeesController(self.main_controller.db_controller)

            # Pobranie wszystkich employee_id i specialty_id z bazy
            all_employee_ids = employees_controller.get_all_employee_ids()
            all_specialty_ids = specialties_controller.get_all_specialty_ids()

            # Sprawdzenie, czy podane ID istnieją w bazie
            if employee_id not in all_employee_ids:
                errors.append(f"Pracownik o Id ({employee_id}) nie istnieje w bazie.")

            if specialty_id not in all_specialty_ids:
                errors.append(f"Specjalność o Id ({specialty_id}) nie istnieje w bazie.")

            # Jeśli są błędy na tym etapie, emitujemy je i przerywamy działanie
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeEmployee_addEmployeeToSpecialty] Błędy walidacji:\n{error_message}")
                self.employeeSpecialtyAdditionFailed.emit(error_message)
                return

            # Pobranie wszystkich przypisań employee_specialty
            existing_employee_specialties = employee_specialties_controller.get_all_employee_specialties()

            # Sprawdzenie, czy podane przypisanie już istnieje
            if any(record["employee_id"] == employee_id and record["specialty_id"] == specialty_id for record in existing_employee_specialties):
                errors.append(f"Pracownik o ID ({employee_id}) jest już przypisany do specjalności o ID ({specialty_id}).")

            # Jeśli są błędy w przypisaniach, emitujemy je i przerywamy działanie
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeEmployee_addEmployeeToSpecialty] Błędy walidacji:\n{error_message}")
                self.employeeSpecialtyAdditionFailed.emit(error_message)
                return

            # Dodanie przypisania do bazy (is_active zawsze = 1)
            employee_specialties_controller.add_employee_specialty(employee_id, specialty_id, is_active=1)

            print("[BridgeEmployee_addEmployeeToSpecialty] Pracownik został przypisany do specjalności pomyślnie!")
            self.employeeSpecialtyAddedSuccessfully.emit()

        except ValueError as ve:
            print(f"[BridgeEmployee_addEmployeeToSpecialty] Błąd wartości: {str(ve)}")
            self.employeeSpecialtyAdditionFailed.emit(str(ve))

        except KeyError as ke:
            print(f"[BridgeEmployee_addEmployeeToSpecialty] Błąd klucza w danych: {str(ke)}")
            self.employeeSpecialtyAdditionFailed.emit("Błąd w strukturze danych.")

        except RuntimeError as re:
            print(f"[BridgeEmployee_addEmployeeToSpecialty] Błąd bazy danych: {str(re)}")
            self.employeeSpecialtyAdditionFailed.emit("Wystąpił błąd bazy danych.")

 # -------------------------------------------------------------------------



    @Slot(str, str, str, str)
    def updateEmployeeService(self, insert_employee_service_id, insert_employee_id, insert_service_id, insert_is_active):
        """
        Aktualizuje przypisanie pracownika do usługi na podstawie ID.
        """
        print(f"[BridgeEmployee_updateEmployeeService] Odebrano dane do aktualizacji: "
            f"EmployeeServiceID={insert_employee_service_id}, EmployeeID={insert_employee_id}, "
            f"ServiceID={insert_service_id}, IsActive={insert_is_active}")

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_updateEmployeeService] Brak zalogowanego użytkownika.")
            self.employeeServiceUpdateFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []  # Lista do zbierania błędów

        # Konwersja ID przypisania usługi do pracownika (pole wymagane)
        try:
            employee_service_id = int(insert_employee_service_id)
        except ValueError:
            errors.append("ID przypisania usługi do pracownika musi być liczbą całkowitą.")

        # Konwersja ID pracownika (pole opcjonalne)
        if insert_employee_id.strip() != "":
            try:
                employee_id = int(insert_employee_id)
            except ValueError:
                errors.append("ID pracownika musi być liczbą całkowitą.")
        else:
            employee_id = None

        # Konwersja ID usługi (pole opcjonalne)
        if insert_service_id.strip() != "":
            try:
                service_id = int(insert_service_id)
            except ValueError:
                errors.append("ID usługi musi być liczbą całkowitą.")
        else:
            service_id = None

        try:
            employee_services_controller = EmployeeServicesController(self.main_controller.db_controller)
            services_controller = ServicesController(self.main_controller.db_controller)
            employees_controller = EmployeesController(self.main_controller.db_controller)

            # Pobranie wszystkich employee_service_id z bazy
            all_employee_service_ids = employee_services_controller.get_all_employee_service_ids()
            if employee_service_id not in all_employee_service_ids:
                errors.append(f"Przypisanie o ID ({employee_service_id}) nie istnieje w bazie.")

            # Pobranie wszystkich employee_id i service_id
            all_employee_ids = employees_controller.get_all_employee_ids()
            all_service_ids = services_controller.get_all_service_ids()

            # Sprawdzenie, czy podane ID istnieją w bazie – tylko dla pól, które zostały podane
            if employee_id is not None and employee_id not in all_employee_ids:
                errors.append(f"Pracownik o ID ({employee_id}) nie istnieje w bazie.")
            if service_id is not None and service_id not in all_service_ids:
                errors.append(f"Usługa o ID ({service_id}) nie istnieje w bazie.")

            # Pobranie wszystkich przypisań employee_service
            existing_employee_services = employee_services_controller.get_all_employee_services()

            # Sprawdzenie, czy podane przypisanie już istnieje
            if any(record["employee_id"] == employee_id and record["service_id"] == service_id for record in existing_employee_services):
                errors.append(f"Pracownik o ID ({employee_id}) jest już przypisany do usługi o ID ({service_id}).")

            # Normalizacja wartości is_active (pole opcjonalne)
            is_active = None
            if insert_is_active.strip() != "":
                normalized_is_active = insert_is_active.strip().lower()
                if normalized_is_active == "tak":
                    is_active = 1
                elif normalized_is_active == "nie":
                    is_active = 0
                else:
                    errors.append("Niepoprawna wartość dla pola 'Aktywność'. Użyj 'Tak' lub 'Nie'.")

            # Jeśli są błędy, wyemituj je i zakończ działanie
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeEmployee_updateEmployeeService] Błędy walidacji:\n{error_message}")
                self.employeeServiceUpdateFailed.emit(error_message)
                return

            # Pobranie istniejącego rekordu przypisania
            existing_data = employee_services_controller.get_record_by_id(employee_service_id)
            if not existing_data:
                self.employeeServiceUpdateFailed.emit(f"Błąd podczas pobierania szczegółów przypisania o ID ({employee_service_id}).")
                return

            # Budowanie słownika danych do aktualizacji – tylko dla pól, które uległy zmianie i zostały podane
            data_to_update = {}
            if employee_id is not None and employee_id != existing_data["employee_id"]:
                data_to_update["employee_id"] = employee_id
            if service_id is not None and service_id != existing_data["service_id"]:
                data_to_update["service_id"] = service_id
            if is_active is not None and is_active != existing_data.get("is_active"):
                data_to_update["is_active"] = is_active

            # Jeśli nie ma zmian, wyemituj komunikat o braku zmian
            if not data_to_update:
                print("[BridgeEmployee_updateEmployeeService] Brak zmian w danych przypisania. Aktualizacja nie została wykonana.")
                self.employeeServiceUpdateFailed.emit("Brak zmian w danych przypisania.")
                return

            # Wywołanie aktualizacji w kontrolerze
            employee_services_controller.update_employee_service(employee_service_id, data_to_update)
            print("[BridgeEmployee_updateEmployeeService] Przypisanie pracownika do usługi zostało zaktualizowane w bazie danych.")
            self.employeeServiceUpdatedSuccessfully.emit()

        except ValueError as ve:
            print(f"[BridgeEmployee_updateEmployeeService] Błąd wartości: {str(ve)}")
            self.employeeServiceUpdateFailed.emit(str(ve))
        except KeyError as ke:
            print(f"[BridgeEmployee_updateEmployeeService] Błąd klucza w danych: {str(ke)}")
            self.employeeServiceUpdateFailed.emit("Błąd w strukturze danych.")
        except RuntimeError as re:
            print(f"[BridgeEmployee_updateEmployeeService] Błąd bazy danych: {str(re)}")
            self.employeeServiceUpdateFailed.emit("Wystąpił błąd bazy danych.")


 # -------------------------------------------------------------------------

    @Slot(str, str, str, str)
    def updateEmployeeSpecialty(self, insert_employee_specialty_id, insert_employee_id, insert_specialty_id, insert_is_active):
        """
        Aktualizuje przypisanie pracownika do specjalności na podstawie ID.
        """
        print(f"[BridgeEmployee_updateEmployeeSpecialty] Odebrano dane do aktualizacji: "
            f"EmployeeSpecialtyID={insert_employee_specialty_id}, EmployeeID={insert_employee_id}, "
            f"SpecialtyID={insert_specialty_id}, IsActive={insert_is_active}")

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_updateEmployeeSpecialty] Brak zalogowanego użytkownika.")
            self.employeeSpecialtyUpdateFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []

        # Konwersja ID przypisania (pole wymagane)
        try:
            employee_specialty_id = int(insert_employee_specialty_id)
        except ValueError:
            errors.append("ID przypisania specjalności musi być liczbą całkowitą.")

        # Konwersja ID pracownika (pole opcjonalne)
        employee_id = None
        if insert_employee_id.strip():
            try:
                employee_id = int(insert_employee_id)
            except ValueError:
                errors.append("ID pracownika musi być liczbą całkowitą.")

        # Konwersja ID specjalności (pole opcjonalne)
        specialty_id = None
        if insert_specialty_id.strip():
            try:
                specialty_id = int(insert_specialty_id)
            except ValueError:
                errors.append("ID specjalności musi być liczbą całkowitą.")

        # Przetwarzanie is_active (pole opcjonalne)
        is_active = None
        if insert_is_active.strip():
            normalized_is_active = insert_is_active.strip().lower()
            if normalized_is_active == "tak":
                is_active = 1
            elif normalized_is_active == "nie":
                is_active = 0
            else:
                errors.append("Niepoprawna wartość dla pola 'Aktywność'. Użyj 'Tak' lub 'Nie'.")

        if errors:
            error_message = "\n".join(errors)
            print(f"[BridgeEmployee_updateEmployeeSpecialty] Błędy walidacji:\n{error_message}")
            self.employeeSpecialtyUpdateFailed.emit(error_message)
            return

        try:
            employee_specialties_controller = EmployeeSpecialtiesController(self.main_controller.db_controller)
            specialties_controller = SpecialtiesController(self.main_controller.db_controller)
            employees_controller = EmployeesController(self.main_controller.db_controller)

            # Sprawdzenie istnienia przypisania
            all_employee_specialty_ids = employee_specialties_controller.get_all_employee_specialty_ids()
            if employee_specialty_id not in all_employee_specialty_ids:
                errors.append(f"Przypisanie o ID {employee_specialty_id} nie istnieje.")

            # Sprawdzenie istnienia pracownika (tylko jeśli podano wartość)
            if insert_employee_id.strip() and employee_id not in employees_controller.get_all_employee_ids():
                errors.append(f"Pracownik o ID {employee_id} nie istnieje.")

            # Sprawdzenie istnienia specjalności (tylko jeśli podano wartość)
            if insert_specialty_id.strip() and specialty_id not in specialties_controller.get_all_specialty_ids():
                errors.append(f"Specjalność o ID {specialty_id} nie istnieje.")

            # Pobranie wszystkich przypisań employee_specialty
            existing_employee_specialties = employee_specialties_controller.get_all_employee_specialties()

            # Sprawdzenie, czy podane przypisanie już istnieje
            if any(record["employee_id"] == employee_id and record["specialty_id"] == specialty_id for record in existing_employee_specialties):
                errors.append(f"Pracownik o ID ({employee_id}) jest już przypisany do specjalności o ID ({specialty_id}).")

            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeEmployee_updateEmployeeSpecialty] Błędy walidacji:\n{error_message}")
                self.employeeSpecialtyUpdateFailed.emit(error_message)
                return

            # Pobranie istniejących danych
            existing_data = employee_specialties_controller.get_employee_specialty_by_id(employee_specialty_id)
            if not existing_data:
                self.employeeSpecialtyUpdateFailed.emit(f"Błąd podczas pobierania przypisania o ID {employee_specialty_id}.")
                return

            # Budowanie danych do aktualizacji
            data_to_update = {}
            if employee_id is not None and employee_id != existing_data["employee_id"]:
                data_to_update["employee_id"] = employee_id
                
            if specialty_id is not None and specialty_id != existing_data["specialty_id"]:
                data_to_update["specialty_id"] = specialty_id
                
            if is_active is not None and is_active != existing_data.get("is_active"):
                data_to_update["is_active"] = is_active

            if not data_to_update:
                print("[BridgeEmployee_updateEmployeeSpecialty] Brak zmian w danych.")
                self.employeeSpecialtyUpdateFailed.emit("Brak zmian w danych.")
                return

            # Aktualizacja w bazie
            employee_specialties_controller.update_employee_specialty(
                employee_specialty_id,
                **data_to_update
            )

            print("[BridgeEmployee_updateEmployeeSpecialty] Przypisanie zaktualizowane pomyślnie.")
            self.employeeSpecialtyUpdatedSuccessfully.emit()

        except ValueError as ve:
            print(f"[BridgeEmployee_updateEmployeeSpecialty] Błąd wartości: {str(ve)}")
            self.employeeSpecialtyUpdateFailed.emit(str(ve))
        except KeyError as ke:
            print(f"[BridgeEmployee_updateEmployeeSpecialty] Błąd klucza w danych: {str(ke)}")
            self.employeeSpecialtyUpdateFailed.emit("Błąd w strukturze danych.")
        except RuntimeError as re:
            print(f"[BridgeEmployee_updateEmployeeSpecialty] Błąd bazy danych: {str(re)}")
            self.employeeSpecialtyUpdateFailed.emit("Wystąpił błąd bazy danych.")



 # -------------------------------------------------------------------------

    @Slot(int)
    def deleteEmployeeSpecialty(self, insert_employee_specialty_id):
        """
        Usuwa przypisanie pracownika do specjalności na podstawie podanego employee_specialty_id.
        """
        print(f"[BridgeEmployee_deleteEmployeeSpecialty] Otrzymano żądanie usunięcia przypisania o ID: {insert_employee_specialty_id}")

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_deleteEmployeeSpecialty] Brak zalogowanego użytkownika.")
            self.employeeSpecialtyDeletionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            employee_specialties_controller = EmployeeSpecialtiesController(self.main_controller.db_controller)

            # Pobranie wszystkich `employee_specialty_id` z bazy
            all_employee_specialty_ids = employee_specialties_controller.get_all_employee_specialty_ids()

            # Sprawdzenie, czy podany `insert_employee_specialty_id` istnieje w bazie
            if insert_employee_specialty_id not in all_employee_specialty_ids:
                msg = f"Przypisanie pracownika do specjalności o ID ({insert_employee_specialty_id}) nie istnieje w bazie."
                print(f"[BridgeEmployee_deleteEmployeeSpecialty] {msg}")
                self.employeeSpecialtyDeletionFailed.emit(msg)
                return

            # Próba usunięcia przypisania
            employee_specialties_controller.delete_employee_specialty(insert_employee_specialty_id)

            print(f"[BridgeEmployee_deleteEmployeeSpecialty] Przypisanie o ID {insert_employee_specialty_id} zostało usunięte.")
            self.employeeSpecialtyDeletedSuccessfully.emit()

        except ValueError as ve:
            print(f"[BridgeEmployee_deleteEmployeeSpecialty] Błąd wartości: {str(ve)}")
            self.employeeSpecialtyDeletionFailed.emit(str(ve))

        except RuntimeError as re:
            print(f"[BridgeEmployee_deleteEmployeeSpecialty] Błąd bazy danych: {str(re)}")
            self.employeeSpecialtyDeletionFailed.emit("Błąd systemu podczas usuwania przypisania.")

        except KeyError as ke:
            print(f"[BridgeEmployee_deleteEmployeeSpecialty] Błąd klucza w danych: {str(ke)}")
            self.employeeSpecialtyDeletionFailed.emit("Błąd w strukturze danych.")

 # -------------------------------------------------------------------------

    @Slot(int)
    def deleteEmployeeService(self, insert_employee_service_id):
        """
        Usuwa przypisanie pracownika do usługi na podstawie podanego employee_service_id.
        """
        print(f"[BridgeEmployee_deleteEmployeeService] Otrzymano żądanie usunięcia przypisania o ID: {insert_employee_service_id}")

        if self._logged_in_user_id is None:
            print("[BridgeEmployee_deleteEmployeeService] Brak zalogowanego użytkownika.")
            self.employeeServiceDeletionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            employee_services_controller = EmployeeServicesController(self.main_controller.db_controller)

            # Pobranie wszystkich `employee_service_id` z bazy
            all_employee_service_ids = employee_services_controller.get_all_employee_service_ids()

            # Sprawdzenie, czy podany `insert_employee_service_id` istnieje w bazie
            if insert_employee_service_id not in all_employee_service_ids:
                msg = f"Przypisanie pracownika do usługi o ID ({insert_employee_service_id}) nie istnieje w bazie."
                print(f"[BridgeEmployee_deleteEmployeeService] {msg}")
                self.employeeServiceDeletionFailed.emit(msg)
                return

            # Próba usunięcia przypisania
            employee_services_controller.delete_record_by_id(insert_employee_service_id)

            print(f"[BridgeEmployee_deleteEmployeeService] Przypisanie o ID {insert_employee_service_id} zostało usunięte.")
            self.employeeServiceDeletedSuccessfully.emit()

        except ValueError as ve:
            print(f"[BridgeEmployee_deleteEmployeeService] Błąd wartości: {str(ve)}")
            self.employeeServiceDeletionFailed.emit(str(ve))

        except RuntimeError as re:
            print(f"[BridgeEmployee_deleteEmployeeService] Błąd bazy danych: {str(re)}")
            self.employeeServiceDeletionFailed.emit("Błąd systemu podczas usuwania przypisania.")

        except KeyError as ke:
            print(f"[BridgeEmployee_deleteEmployeeService] Błąd klucza w danych: {str(ke)}")
            self.employeeServiceDeletionFailed.emit("Błąd w strukturze danych.")
