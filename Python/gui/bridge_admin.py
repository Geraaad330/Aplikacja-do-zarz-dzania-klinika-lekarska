        
import bcrypt
import sqlite3
import re
from PySide6.QtCore import QObject, Signal, Slot# pylint: disable=E0611
from controllers.users_accounts_controller import UsersAccountsController
from controllers.patients_controller import PatientController
from controllers.assigned_patients_controller import AssignedPatientsController
from controllers.roles_controller import RolesController
from services.admin_service import AdminService
from datetime import datetime


class BridgeAdmin(QObject):
    userListChanged = Signal(list)
    rolesListChanged = Signal(list)
    assignedPatientsListChanged = Signal(list)
    userAdditionFailed = Signal(str) 
    userAddedSuccessfully = Signal()  
    userUpdateFailed = Signal(str)  
    userUpdatedSuccessfully = Signal() 
    userDeletionFailed = Signal(str) 
    userDeletedSuccessfully = Signal()
    patientAssignmentFailed = Signal(str) 
    patientAssignedSuccessfully = Signal()
    patientAssignmentUpdatedSuccessfully = Signal()
    patientAssignmentUpdateFailed = Signal(str)
    patientAssignmentDeletedSuccessfully = Signal()
    patientAssignmentDeletionFailed = Signal(str)
    roleAddedSuccessfully = Signal()
    roleAdditionFailed = Signal(str)
    roleUpdatedSuccessfully = Signal()
    roleUpdateFailed = Signal(str)
    roleDeletedSuccessfully = Signal()
    roleDeletionFailed = Signal(str)

    def __init__(self, main_controller):
        try:
            super().__init__()
            print("BridgeAdmin initialized")  # Debugging
            self.main_controller = main_controller
            self._logged_in_user_id = None
            self._user_list = []
            self._roles_list = []
            self._assigned_patients_list = []
        except AttributeError as e:
            print(f"Błąd w __init__: {str(e)} - problem z atrybutami")
        except TypeError as e:
            print(f"Błąd w __init__: {str(e)} - problem z typami danych")

 # -------------------------------------------------------------------------

    @Slot()
    def updateUserList(self):
        """
        Pobiera listę użytkowników z admin_service i emituje sygnał do QML.
        """
        try:
            admin_service = AdminService(self.main_controller)
            # Pobranie listy użytkowników z admin_service
            user_list = admin_service.get_all_user_accounts()


            if not isinstance(user_list, list):
                print("[BridgeAdmin_updateUserList] Nieprawidłowy format danych użytkowników.")
                self.userListChanged.emit([])  # Emituj pustą listę w przypadku błędu
                return

            # Aktualizacja lokalnej listy użytkowników
            self._user_list = user_list

            # Emitowanie sygnału z listą użytkowników
            self.userListChanged.emit(self._user_list)

        except KeyError as ke:
            print(f"[BridgeAdmin_updateUserList] Błąd klucza w danych użytkowników: {ke}")
            self.userListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except ValueError as ve:
            print(f"[BridgeAdmin_updateUserList] Nieprawidłowa wartość w danych użytkowników: {ve}")
            self.userListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except TypeError as te:
            print(f"[BridgeAdmin_updateUserList] Błąd typu danych użytkowników: {te}")
            self.userListChanged.emit([])  # Emituj pustą listę w przypadku błędu

    @Slot(result=list)
    def getUserList(self):
        """
        Zwraca aktualną listę użytkowników.
        """
        return self._user_list
    
 # -------------------------------------------------------------------------

    @Slot()
    def updateRolesList(self):
        """
        Pobiera listę ról z admin_service i emituje sygnał do QML.
        """
        try:
            # Pobranie listy ról z admin_service
            admin_service = AdminService(self.main_controller)
            roles_list = admin_service.get_all_roles()

            if not isinstance(roles_list, list):
                print("[BridgeAdmin_updateRolesList] Nieprawidłowy format danych ról.")
                self.rolesListChanged.emit([])  # Emituj pustą listę w przypadku błędu
                return

            # Aktualizacja lokalnej listy ról
            self._roles_list = roles_list

            # Emitowanie sygnału z listą ról
            self.rolesListChanged.emit(self._roles_list)

        except KeyError as ke:
            print(f"[BridgeAdmin_updateRolesList] Błąd klucza w danych ról: {ke}")
            self.rolesListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except ValueError as ve:
            print(f"[BridgeAdmin_updateRolesList] Nieprawidłowa wartość w danych ról: {ve}")
            self.rolesListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except TypeError as te:
            print(f"[BridgeAdmin_updateRolesList] Błąd typu danych ról: {te}")
            self.rolesListChanged.emit([])  # Emituj pustą listę w przypadku błędu

    @Slot(result=list)
    def getRolesList(self):
        """
        Zwraca aktualną listę ról.
        """
        return self._roles_list
    
# -------------------------------------------------------------------------

    @Slot()
    def updateAssignedPatientsList(self):
        """
        Pobiera listę przypisanych pacjentów z admin_service i emituje sygnał do QML.
        """
        try:
            # Pobranie listy przypisanych pacjentów z admin_service
            admin_service = AdminService(self.main_controller)
            assigned_patients_list = admin_service.get_all_assigned_patients()

            if not isinstance(assigned_patients_list, list):
                print("[BridgeAdmin_updateAssignedPatientsList] Nieprawidłowy format danych przypisanych pacjentów.")
                self.assignedPatientsListChanged.emit([])  # Emituj pustą listę w przypadku błędu
                return

            # Aktualizacja lokalnej listy przypisanych pacjentów
            self._assigned_patients_list = assigned_patients_list

            # Emitowanie sygnału z listą przypisanych pacjentów
            self.assignedPatientsListChanged.emit(self._assigned_patients_list)

        except KeyError as ke:
            print(f"[BridgeAdmin_updateAssignedPatientsList] Błąd klucza w danych przypisanych pacjentów: {ke}")
            self.assignedPatientsListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except ValueError as ve:
            print(f"[BridgeAdmin_updateAssignedPatientsList] Nieprawidłowa wartość w danych przypisanych pacjentów: {ve}")
            self.assignedPatientsListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except TypeError as te:
            print(f"[BridgeAdmin_updateAssignedPatientsList] Błąd typu danych przypisanych pacjentów: {te}")
            self.assignedPatientsListChanged.emit([])  # Emituj pustą listę w przypadku błędu

    @Slot(result=list)
    def getAssignedPatientsList(self):
        """
        Zwraca aktualną listę przypisanych pacjentów.
        """
        return self._assigned_patients_list
    

 # -------------------------------------------------------------------------

    @Slot(int, int, str, str, str)
    def addInternalUser(self, insert_employee_id, insert_role_id, insert_username, insert_password, insert_expired_date):
        """
        Dodaje użytkownika wewnętrznego do systemu po zweryfikowaniu poprawności danych.

        :param insert_employee_id: ID pracownika.
        :param insert_role_id: ID roli.
        :param insert_username: Nazwa użytkownika.
        :param insert_password: Hasło użytkownika.
        :param insert_expired_date: Data wygaśnięcia konta (YYYY-MM-DD).
        """
        print(f"[BridgeRoom_addInternalUser] Otrzymano dane: EmployeeID={insert_employee_id}, RoleID={insert_role_id}, Username={insert_username}, ExpiredDate={insert_expired_date}")

        errors = []  # Lista błędów walidacyjnych

        try:

            admin_service = AdminService(self.main_controller)
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)

            # Pobranie listy employee_id, role_id, username oraz użytych employee_id z users_accounts
            all_employee_ids = admin_service.get_all_employee_ids()
            all_employee_ids_from_users_accounts = admin_service.get_all_employee_ids_from_users_accounts()
            all_role_ids = admin_service.get_all_role_ids()
            all_usernames = admin_service.get_all_usernames()

            # **Sprawdzenie warunków dla `insert_employee_id`**
            if insert_employee_id not in all_employee_ids:
                errors.append(f"Pracownik o ID {insert_employee_id} nie istnieje w systemie.")
            elif insert_employee_id in all_employee_ids and insert_employee_id in all_employee_ids_from_users_accounts:
                available_ids = [emp_id for emp_id in all_employee_ids if emp_id not in all_employee_ids_from_users_accounts]
                errors.append(f"Pracownik o ID {insert_employee_id} istnieje już w users_accounts. Dostępne employee_id do przypisania: {available_ids}")
            elif insert_employee_id not in all_employee_ids_from_users_accounts:
                print(f"[BridgeRoom_addInternalUser] Pracownik o ID {insert_employee_id} jest dostępny do przypisania.")

            # **Sprawdzenie czy `insert_role_id` istnieje**
            if insert_role_id not in all_role_ids:
                errors.append(f"Rola o ID {insert_role_id} nie istnieje w systemie.")

            # **Sprawdzenie czy `insert_username` już istnieje**
            if insert_username in all_usernames:
                errors.append(f"Nazwa użytkownika '{insert_username}' jest już zajęta.")

             # **Walidacja nazwy użytkownika (`insert_username`)**
            username_regex = r'^[a-z]+[.][a-z]+$'
            if not re.match(username_regex, insert_username) or len(insert_username) < 3:
                errors.append("Nazwa użytkownika musi składać się tylko z małych liter, zawierać kropkę (.), nie może zawierać spacji, liczb ani znaków specjalnych i musi mieć co najmniej 3 znaki.")

            # **Walidacja hasła (`insert_password`)**
            password_regex = r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
            if not re.match(password_regex, insert_password):
                errors.append("Hasło musi zawierać co najmniej: jedną dużą literę, jedną cyfrę, jeden znak specjalny i mieć co najmniej 8 znaków.")

           

            # **Walidacja daty wygasania**
            try:
                # Sprawdzenie, czy format pasuje do "YYYY-MM-DD HH:MM"
                expired_date = datetime.strptime(insert_expired_date, "%Y-%m-%d %H:%M")

                # Sprawdzenie, czy data jest w przyszłości
                if expired_date <= datetime.now():
                    errors.append("Data wygasania konta musi być datą przyszłą.")

                # Sformatowanie daty do wymaganego formatu "YYYY-MM-DD HH:MM"
                expired_date = expired_date.strftime("%Y-%m-%d %H:%M")

            except ValueError:
                errors.append("Niepoprawny format daty wygasania. Oczekiwano formatu YYYY-MM-DD HH:MM.")

            # **Jeśli są błędy, emitujemy je i przerywamy działanie**
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_addInternalUser] Błędy walidacji:\n{error_message}")
                self.userAdditionFailed.emit(error_message)
                return

            # **Hashowanie hasła przy użyciu bcrypt**
            hashed_password = bcrypt.hashpw(insert_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # **Ustawienie pozostałych wartości**
            is_active = 1  # Konto zawsze aktywne na start
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M")  # FORMAT ZGODNY Z CHECK
            last_login = None  # Brak logowania na start

            # **Dodanie użytkownika do bazy danych**
            success = users_accounts_controller.add_user_by_ids(
                employee_id=insert_employee_id,
                role_id=insert_role_id,
                username=insert_username,
                password_hash=hashed_password,
                is_active=is_active,
                created_at=created_at,
                last_login=last_login,
                expired=insert_expired_date
            )

            if success:
                print(f"[BridgeRoom_addInternalUser] Użytkownik został dodany pomyślnie! Username: {insert_username}")
                self.userAddedSuccessfully.emit()
            else:
                print("[BridgeRoom_addInternalUser] Nie udało się dodać użytkownika do systemu.")
                self.userAdditionFailed.emit("Wystąpił problem podczas dodawania użytkownika.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_addInternalUser] Błąd operacyjny bazy danych: {str(op_err)}")
            self.userAdditionFailed.emit("Błąd operacyjny bazy danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_addInternalUser] Błąd bazy danych: {str(db_err)}")
            self.userAdditionFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_addInternalUser] Błąd klucza w danych: {str(ke)}")
            self.userAdditionFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_addInternalUser] Błąd przetwarzania danych: {str(te)}")
            self.userAdditionFailed.emit("Błąd przetwarzania danych.")

 # -------------------------------------------------------------------------


    @Slot(int, int, int, str, str, str, str)
    def updateUser(self, insert_user_id, insert_employee_id=0, insert_role_id=0, insert_username="", insert_password="", insert_expired_date="", insert_is_active=""):
        """
        Aktualizuje dane użytkownika w systemie na podstawie podanych parametrów.
        Parametr insert_user_id jest wymagany.
        Pozostałe parametry są opcjonalne – aktualizacja nastąpi tylko dla pól, które mają przekazaną wartość.

        :param insert_user_id: ID użytkownika do aktualizacji.
        :param insert_employee_id: Nowe ID pracownika.
        :param insert_role_id: Nowe ID roli.
        :param insert_username: Nowa nazwa użytkownika.
        :param insert_password: Nowe hasło użytkownika.
        :param insert_expired_date: Nowa data wygaśnięcia konta (YYYY-MM-DD HH:MM).
        :param insert_is_active: Nowa wartość aktywności ("tak"/"nie").
        """
        print(f"[BridgeRoom_updateUser] Otrzymano dane: UserID={insert_user_id}, EmployeeID={insert_employee_id}, RoleID={insert_role_id}, Username={insert_username}, Password={'***' if insert_password else None}, ExpiredDate={insert_expired_date}, isActive={insert_is_active}")
        errors = []

        try:
            admin_service = AdminService(self.main_controller)
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
            
            # *** Walidacja insert_user_id ***
            all_user_ids = admin_service.get_all_user_ids()


            if insert_user_id not in all_user_ids:
                self.userUpdateFailed.emit(f"Użytkownik o podanym ID {insert_user_id} nie istnieje w systemie.")
                return

            # Pobranie obecnych danych użytkownika
            current_data = users_accounts_controller.get_user_by_id(insert_user_id)
            if current_data is None:
                self.userUpdateFailed.emit("Użytkownik o podanym ID nie istnieje w systemie.")
                return

            update_data = {}

            # Aktualizacja pola insert_employee_id (przekazujemy int, 0 oznacza brak wartości)
            if insert_employee_id != 0:
                all_employee_ids = admin_service.get_all_employee_ids()
                all_employee_ids_from_users_accounts = admin_service.get_all_employee_ids_from_users_accounts()
                if insert_employee_id not in all_employee_ids:
                    errors.append(f"Pracownik o ID {insert_employee_id} nie istnieje w systemie.")
                elif insert_employee_id in all_employee_ids and insert_employee_id in all_employee_ids_from_users_accounts:
                    available_ids = [emp_id for emp_id in all_employee_ids if emp_id not in all_employee_ids_from_users_accounts]
                    errors.append(f"Pracownik o ID {insert_employee_id} jest już przypisany. Dostępne employee_id: {available_ids}")
                else:
                    if current_data.get('employee_id') == insert_employee_id:
                        print(f"[BridgeRoom_updateUser] insert_employee_id jest taki sam jak obecny: {insert_employee_id}")
                    else:
                        update_data['employee_id'] = insert_employee_id

            # Aktualizacja pola insert_role_id (przekazujemy int, 0 oznacza brak wartości)
            if insert_role_id != 0:
                all_role_ids = admin_service.get_all_role_ids()
                if insert_role_id not in all_role_ids:
                    errors.append(f"Rola o ID {insert_role_id} nie istnieje w systemie.")
                else:
                    if current_data.get('role_id') == insert_role_id:
                        print("[BridgeRoom_updateUser] insert_role_id jest taki sam jak obecny.")
                    else:
                        update_data['role_id'] = insert_role_id

            # Aktualizacja pola insert_username
            if insert_username != "":
                all_usernames = admin_service.get_all_usernames()
                if insert_username != current_data.get('username') and insert_username in all_usernames:
                    errors.append(f"Nazwa użytkownika '{insert_username}' jest już zajęta.")
                username_regex = r'^[a-z]+[.][a-z]+$'
                if not re.match(username_regex, insert_username) or len(insert_username) < 3:
                    errors.append("Nazwa użytkownika musi składać się tylko z małych liter, zawierać kropkę (.), nie może zawierać spacji, liczb ani znaków specjalnych i musi mieć co najmniej 3 znaki.")
                else:
                    if current_data.get('username') == insert_username:
                        print("[BridgeRoom_updateUser] insert_username jest taki sam jak obecny.")
                    else:
                        update_data['username'] = insert_username

            # Aktualizacja pola insert_password
            if insert_password != "":
                password_regex = r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
                if not re.match(password_regex, insert_password):
                    errors.append("Hasło musi zawierać co najmniej: jedną dużą literę, jedną cyfrę, jeden znak specjalny i mieć co najmniej 8 znaków.")
                else:
                    hashed_password = bcrypt.hashpw(insert_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    current_hash = current_data.get('password_hash')
                    if current_hash is not None:
                        if bcrypt.checkpw(insert_password.encode('utf-8'), current_hash.encode('utf-8')):
                            print("[BridgeRoom_updateUser] insert_password jest taki sam jak obecny.")
                        else:
                            update_data['password_hash'] = hashed_password
                    else:
                        update_data['password_hash'] = hashed_password


            # Aktualizacja pola insert_expired_date
            if insert_expired_date != "":
                try:
                    # Sprawdzenie formatu daty: YYYY-MM-DD HH:MM
                    expired_date_obj = datetime.strptime(insert_expired_date, "%Y-%m-%d %H:%M")
                    if expired_date_obj <= datetime.now():
                        errors.append("Data wygasania konta musi być datą przyszłą.")
                    else:
                        if current_data.get('expired') == insert_expired_date:
                            print("[BridgeRoom_updateUser] insert_expired_date jest taki sam jak obecny.")
                        else:
                            update_data['expired'] = insert_expired_date
                except ValueError:
                    errors.append("Niepoprawny format daty wygasania. Oczekiwano formatu YYYY-MM-DD HH:MM.")

            # Aktualizacja pola insert_is_active
            if insert_is_active != "":
                if isinstance(insert_is_active, str):
                    # Używamy metody lower() (a nie toLowerCase()) dla porównania niewrażliwego na wielkość liter
                    normalized_input = insert_is_active.strip().lower()
                    if normalized_input == "tak":
                        normalized_active = 1
                    elif normalized_input == "nie":
                        normalized_active = 0
                    else:
                        errors.append("Wartość is_active musi być 'tak' lub 'nie'.")
                        normalized_active = None
                else:
                    normalized_active = insert_is_active

                if normalized_active is not None:
                    if current_data.get('is_active') == normalized_active:
                        print("[BridgeRoom_updateUser] insert_is_active jest taki sam jak obecny.")
                    else:
                        update_data['is_active'] = normalized_active

            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_updateUser] Błędy walidacji:\n{error_message}")
                self.userUpdateFailed.emit(error_message)
                return

            if not update_data:
                self.userUpdateFailed.emit("Brak zmian w danych do aktualizacji.")
                return

            try:
                success = users_accounts_controller.update_user_by_ids(insert_user_id, **update_data)
                if success:
                    print(f"[BridgeRoom_updateUser] Użytkownik o ID {insert_user_id} został zaktualizowany pomyślnie.")
                    self.userUpdatedSuccessfully.emit()
                else:
                    print("[BridgeRoom_updateUser] Nie udało się zaktualizować użytkownika.")
                    self.userUpdateFailed.emit("Wystąpił problem podczas aktualizacji użytkownika.")
            except sqlite3.OperationalError as op_err:
                print(f"[BridgeRoom_updateUser] Błąd operacyjny bazy danych: {str(op_err)}")
                self.userUpdateFailed.emit("Błąd operacyjny bazy danych.")
            except sqlite3.DatabaseError as db_err:
                print(f"[BridgeRoom_updateUser] Błąd bazy danych: {str(db_err)}")
                self.userUpdateFailed.emit("Błąd bazy danych.")
            except KeyError as ke:
                print(f"[BridgeRoom_updateUser] Błąd klucza w danych: {str(ke)}")
                self.userUpdateFailed.emit("Błąd w strukturze danych.")
            except TypeError as te:
                print(f"[BridgeRoom_updateUser] Błąd przetwarzania danych: {str(te)}")
                self.userUpdateFailed.emit("Błąd przetwarzania danych.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_updateUser] Błąd operacyjny bazy danych: {str(op_err)}")
            self.userUpdateFailed.emit("Błąd operacyjny bazy danych.")
        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_updateUser] Błąd bazy danych: {str(db_err)}")
            self.userUpdateFailed.emit("Błąd bazy danych.")

 # -------------------------------------------------------------------------


    @Slot(int)
    def deleteUser(self, insert_user_id):
        """
        Usuwa użytkownika na podstawie podanego user_id.

        :param insert_user_id: ID użytkownika do usunięcia.
        """
        print(f"[BridgeAdmin_deleteUser] Otrzymano żądanie usunięcia użytkownika o ID: {insert_user_id}")

        try:
            admin_service = AdminService(self.main_controller)
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)

            # **Pobranie wszystkich user_id z bazy**
            all_user_ids = admin_service.get_all_user_ids()

            # **Sprawdzenie, czy `insert_user_id` istnieje w bazie**
            if insert_user_id not in all_user_ids:
                msg = f"Użytkownik o ID ({insert_user_id}) nie istnieje w bazie."
                print(f"[BridgeAdmin_deleteUser] {msg}")
                self.userDeletionFailed.emit(msg)
                return

            # **Próba usunięcia użytkownika**
            success = users_accounts_controller.delete_user(insert_user_id)

            if success:
                print(f"[BridgeAdmin_deleteUser] Użytkownik o ID {insert_user_id} został usunięty.")
                self.userDeletedSuccessfully.emit()
            else:
                print("[BridgeAdmin_deleteUser] Nie udało się usunąć użytkownika.")
                self.userDeletionFailed.emit("Nie udało się usunąć użytkownika.")

        except ValueError as ve:
            print(f"[BridgeAdmin_deleteUser] Błąd wartości: {str(ve)}")
            self.userDeletionFailed.emit(str(ve))

        except RuntimeError as rue:
            print(f"[BridgeAdmin_deleteUser] Błąd bazy danych: {str(rue)}")
            self.userDeletionFailed.emit("Błąd systemu podczas usuwania użytkownika.")

        except KeyError as ke:
            print(f"[BridgeAdmin_deleteUser] Błąd klucza w danych: {str(ke)}")
            self.userDeletionFailed.emit("Błąd w strukturze danych.")


 # -------------------------------------------------------------------------


    @Slot(int, int)
    def addAssignedPatient(self, insert_patient_id, insert_employee_id):
        """
        Dodaje przypisanie pacjenta do pracownika po zweryfikowaniu poprawności danych.

        :param insert_employee_id: ID pracownika.
        :param insert_patient_id: ID pacjenta.
        """
        print(f"[BridgeRoom_addAssignedPatient] Otrzymano dane: EmployeeID={insert_employee_id}, PatientID={insert_patient_id}")

        errors = []  # Lista błędów walidacyjnych

        try:
            # Inicjalizacja kontrolerów
            admin_service = AdminService(self.main_controller)
            patients_controller = PatientController(self.main_controller.db_controller)
            assigned_patients_controller = AssignedPatientsController(self.main_controller.db_controller)

            # Pobranie listy patient_id, employee_id oraz przypisanych pacjent-pracownik
            all_patient_ids = patients_controller.get_all_patient_ids()
            all_employee_ids = admin_service.get_all_employee_ids()
            assigned_patients = admin_service.get_all_assigned_patients()

            # **Sprawdzenie czy `insert_patient_id` istnieje w bazie**
            if insert_patient_id not in all_patient_ids:
                errors.append(f"Pacjent o ID {insert_patient_id} nie istnieje w systemie.")

            # **Sprawdzenie czy `insert_employee_id` istnieje w bazie**
            if insert_employee_id not in all_employee_ids:
                errors.append(f"Pracownik o ID {insert_employee_id} nie istnieje w systemie.")

            # **Sprawdzenie, czy pacjent ma już przypisanego pracownika**
            for assigned in assigned_patients:
                if assigned["fk_patient_id"] == insert_patient_id:
                    if assigned["is_active"] == 1:
                        errors.append(
                            f"Pacjent o ID {insert_patient_id} ma już aktywnie przypisanego pracownika o ID {assigned['fk_employee_id']}."
                        )
                    elif assigned["is_active"] == 0:
                        print(
                            f"[BridgeRoom_addAssignedPatient] Pacjent {insert_patient_id} miał wcześniej przypisanego pracownika "
                            f"o ID {assigned['fk_employee_id']}, ale przypisanie było nieaktywne. Przechodzimy dalej..."
                        )

            # **Sprawdzenie czy kombinacja `insert_patient_id` i `insert_employee_id` już istnieje**
            for assigned in assigned_patients:
                if assigned["fk_patient_id"] == insert_patient_id and assigned["fk_employee_id"] == insert_employee_id:
                    errors.append(f"Kombinacja pacjenta o ID {insert_patient_id} i pracownika o ID {insert_employee_id} już istnieje.")

            # **Jeśli są błędy, emitujemy je i przerywamy działanie**
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_addAssignedPatient] Błędy walidacji:\n{error_message}")
                self.patientAssignmentFailed.emit(error_message)
                return

            # **Ustawienie wartości aktywności**
            is_active = 1  # Konto zawsze aktywne na start

            # **Dodanie przypisania do bazy danych**
            success = assigned_patients_controller.add_record_by_ids(
                fk_employee_id=insert_employee_id,
                fk_patient_id=insert_patient_id,
                is_active=is_active
            )

            if success:
                print(f"[BridgeRoom_addAssignedPatient] Pacjent {insert_patient_id} został przypisany do pracownika {insert_employee_id}.")
                self.patientAssignedSuccessfully.emit()
            else:
                print("[BridgeRoom_addAssignedPatient] Nie udało się przypisać pacjenta do pracownika.")
                self.patientAssignmentFailed.emit("Nie udało się przypisać pacjenta do pracownika.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_addAssignedPatient] Błąd operacyjny bazy danych: {str(op_err)}")
            self.patientAssignmentFailed.emit("Błąd operacyjny bazy danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_addAssignedPatient] Błąd bazy danych: {str(db_err)}")
            self.patientAssignmentFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_addAssignedPatient] Błąd klucza w danych: {str(ke)}")
            self.patientAssignmentFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_addAssignedPatient] Błąd przetwarzania danych: {str(te)}")
            self.patientAssignmentFailed.emit("Błąd przetwarzania danych.")


 # -------------------------------------------------------------------------


    @Slot(int, int, int, str)
    def updateAssignedPatient(self, insert_assignment_id, insert_patient_id=0, insert_employee_id=0, insert_is_active=""):
        """
        Aktualizuje przypisanie pacjenta do pracownika.

        :param insert_assignment_id: ID przypisania (wymagane).
        :param insert_patient_id: Nowe ID pacjenta (opcjonalne).
        :param insert_employee_id: Nowe ID pracownika (opcjonalne).
        :param insert_is_active: Nowy status aktywności ("tak"/"nie") (opcjonalne).
        """
        print(f"[BridgeRoom_updateAssignedPatient] Otrzymano dane: AssignmentID={insert_assignment_id}, "
            f"PatientID={insert_patient_id}, EmployeeID={insert_employee_id}, isActive={insert_is_active}")
        
        errors = []

        try:
            # Inicjalizacja kontrolerów
            patients_controller = PatientController(self.main_controller.db_controller)
            admin_service = AdminService(self.main_controller)
            assigned_patients_controller = AssignedPatientsController(self.main_controller.db_controller)

            # Sprawdzenie czy insert_assignment_id istnieje w bazie (get_all_assignment_ids)
            all_assignment_ids = admin_service.get_all_assignment_ids()
            if insert_assignment_id not in all_assignment_ids:
                self.patientAssignmentUpdateFailed.emit(
                    f"Przypisanie pacjenta o ID {insert_assignment_id} nie istnieje w systemie."
                )
                return

            # Pobranie istniejących danych przypisania
            current_data = assigned_patients_controller.get_assigned_patient_by_id(insert_assignment_id)
            if current_data is None:
                self.patientAssignmentUpdateFailed.emit(
                    f"Przypisanie pacjenta o ID {insert_assignment_id} nie istnieje w systemie."
                )
                return

            update_data = {}

            # Pobranie listy pacjentów, pracowników i przypisań
            all_patient_ids = patients_controller.get_all_patient_ids()
            all_employee_ids = admin_service.get_all_employee_ids()
            all_assigned_patients = admin_service.get_all_assigned_patients()

            # Sprawdzenie, czy pacjent już ma aktywne przypisanie do jakiegokolwiek pracownika
            for record in all_assigned_patients:
                if record["fk_patient_id"] == insert_patient_id:
                    if record["is_active"] == 1:
                        errors.append(
                            f"Pacjent o ID {insert_patient_id} ma już aktywnie przypisanego pracownika o ID {record['fk_employee_id']}."
                        )
                    elif record["is_active"] == 0:
                        print(
                            f"[BridgeRoom_updateAssignedPatient] Pacjent {insert_patient_id} miał wcześniej przypisanego pracownika "
                            f"o ID {record['fk_employee_id']}, ale przypisanie było nieaktywne. Przechodzimy dalej..."
                        )

            # Walidacja insert_employee_id
            if insert_employee_id != 0:
                if insert_employee_id not in all_employee_ids:
                    errors.append(f"Pracownik o ID {insert_employee_id} nie istnieje w systemie.")
                elif current_data.get("fk_employee_id") != insert_employee_id:
                    update_data["fk_employee_id"] = insert_employee_id

            # Walidacja insert_patient_id
            if insert_patient_id != 0:
                if insert_patient_id not in all_patient_ids:
                    errors.append(f"Pacjent o ID {insert_patient_id} nie istnieje w systemie.")
                elif current_data.get("fk_patient_id") != insert_patient_id:
                    update_data["fk_patient_id"] = insert_patient_id

            # Sprawdzenie unikalności kombinacji insert_patient_id i insert_employee_id
            if insert_patient_id != 0 and insert_employee_id != 0:
                for record in all_assigned_patients:
                    # Pomijamy rekord, który aktualnie aktualizujemy
                    if record.get("assignment_id") != insert_assignment_id:
                        if record.get("fk_patient_id") == insert_patient_id and record.get("fk_employee_id") == insert_employee_id:
                            errors.append(f"Kombinacja pacjenta {insert_patient_id} i pracownika {insert_employee_id} już istnieje.")
                            break

            # Normalizacja wartości insert_is_active
            if insert_is_active != "":
                normalized_input = insert_is_active.strip().lower()
                if normalized_input == "tak":
                    normalized_active = 1
                elif normalized_input == "nie":
                    normalized_active = 0
                else:
                    errors.append("Wartość is_active musi być 'tak' lub 'nie'.")
                    normalized_active = None

                if normalized_active is not None and current_data.get("is_active") != normalized_active:
                    update_data["is_active"] = normalized_active

            # Obsługa błędów walidacji
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_updateAssignedPatient] Błędy walidacji:\n{error_message}")
                self.patientAssignmentUpdateFailed.emit(error_message)
                return

            # Sprawdzenie czy występują zmiany względem aktualnych danych
            if not update_data:
                self.patientAssignmentUpdateFailed.emit("Brak zmian w danych do aktualizacji.")
                return

            # Próba wykonania aktualizacji w bazie
            success = assigned_patients_controller.update_record_by_ids(insert_assignment_id, **update_data)
            if success:
                print(f"[BridgeRoom_updateAssignedPatient] Przypisanie pacjenta o ID {insert_assignment_id} zostało zaktualizowane.")
                self.patientAssignmentUpdatedSuccessfully.emit()
            else:
                print("[BridgeRoom_updateAssignedPatient] Nie udało się zaktualizować przypisania pacjenta.")
                self.patientAssignmentUpdateFailed.emit("Nie udało się zaktualizować przypisania pacjenta.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_updateAssignedPatient] Błąd operacyjny bazy danych: {str(op_err)}")
            self.patientAssignmentUpdateFailed.emit("Błąd operacyjny bazy danych.")
        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_updateAssignedPatient] Błąd bazy danych: {str(db_err)}")
            self.patientAssignmentUpdateFailed.emit("Błąd bazy danych.")
        except KeyError as ke:
            print(f"[BridgeRoom_updateAssignedPatient] Błąd klucza w danych: {str(ke)}")
            self.patientAssignmentUpdateFailed.emit("Błąd w strukturze danych.")
        except TypeError as te:
            print(f"[BridgeRoom_updateAssignedPatient] Błąd przetwarzania danych: {str(te)}")
            self.patientAssignmentUpdateFailed.emit("Błąd przetwarzania danych.")


 # -------------------------------------------------------------------------

    @Slot(int)
    def deleteAssignedPatient(self, insert_assignment_id):
        """
        Usuwa przypisanie pacjenta na podstawie podanego assignment_id.

        :param insert_assignment_id: ID przypisania do usunięcia.
        """
        print(f"[BridgeAdmin_deleteAssignedPatient] Otrzymano żądanie usunięcia przypisania o ID: {insert_assignment_id}")

        try:
            admin_service = AdminService(self.main_controller)
            assigned_patients_controller = AssignedPatientsController(self.main_controller.db_controller)

            # **Pobranie wszystkich assignment_id z bazy**
            all_assignment_ids = admin_service.get_all_assignment_ids()

            # **Sprawdzenie, czy `insert_assignment_id` istnieje w bazie**
            if insert_assignment_id not in all_assignment_ids:
                msg = f"Przypisanie o ID ({insert_assignment_id}) nie istnieje w bazie."
                print(f"[BridgeAdmin_deleteAssignedPatient] {msg}")
                self.patientAssignmentDeletionFailed.emit(msg)
                return

            # **Pobranie wszystkich `fk_assignment_id` z tabeli `appointments`**
            all_fk_assignment_ids = admin_service.get_all_fk_assignment_ids()

            # **Sprawdzenie, czy `insert_assignment_id` jest używane w `appointments`**
            if insert_assignment_id in all_fk_assignment_ids:
                msg = f"Nie można usunąć przypisania o ID ({insert_assignment_id}), ponieważ jest ono powiązane z wizytami."
                print(f"[BridgeAdmin_deleteAssignedPatient] {msg}")
                self.patientAssignmentDeletionFailed.emit(msg)
                return

            # **Próba usunięcia przypisania**
            success = assigned_patients_controller.delete_record_by_id(insert_assignment_id)

            if success:
                print(f"[BridgeAdmin_deleteAssignedPatient] Przypisanie o ID {insert_assignment_id} zostało usunięte.")
                self.patientAssignmentDeletedSuccessfully.emit()
            else:
                print("[BridgeAdmin_deleteAssignedPatient] Nie udało się usunąć przypisania.")
                self.patientAssignmentDeletionFailed.emit("Nie udało się usunąć przypisania.")

        except ValueError as ve:
            print(f"[BridgeAdmin_deleteAssignedPatient] Błąd wartości: {str(ve)}")
            self.patientAssignmentDeletionFailed.emit(str(ve))

        except RuntimeError as rue:
            print(f"[BridgeAdmin_deleteAssignedPatient] Błąd bazy danych: {str(rue)}")
            self.patientAssignmentDeletionFailed.emit("Błąd systemu podczas usuwania przypisania.")

        except KeyError as ke:
            print(f"[BridgeAdmin_deleteAssignedPatient] Błąd klucza w danych: {str(ke)}")
            self.patientAssignmentDeletionFailed.emit("Błąd w strukturze danych.")

 # -------------------------------------------------------------------------

    @Slot(str)
    def addRole(self, insert_role_name):
        """
        Dodaje nową rolę do systemu po zweryfikowaniu poprawności danych.

        :param insert_role_name: Nazwa roli.
        """
        print(f"[BridgeRoom_addRole] Otrzymano dane: RoleName={insert_role_name}")

        try:
            # Inicjalizacja kontrolerów
            admin_service = AdminService(self.main_controller)
            roles_controller = RolesController(self.main_controller.db_controller)

            # Pobranie listy dostępnych ról
            all_role_names = admin_service.get_all_role_names()

            # **Walidacja `insert_role_name`**
            normalized_role_name = insert_role_name.strip().capitalize()  # Konwersja np. "KIEROWNIK" → "Kierownik"

            if normalized_role_name in [role.capitalize() for role in all_role_names]:
                msg = f"Rola '{insert_role_name}' istnieje w systemie."
                print(f"[BridgeRoom_addRole] {msg}")
                self.roleAdditionFailed.emit(msg)
                return

            # **Dodanie roli do bazy danych**
            success = roles_controller.add_role(normalized_role_name)

            if success:
                print(f"[BridgeRoom_addRole] Rola '{normalized_role_name}' została dodana pomyślnie.")
                self.roleAddedSuccessfully.emit()
            else:
                print("[BridgeRoom_addRole] Nie udało się dodać roli.")
                self.roleAdditionFailed.emit("Nie udało się dodać roli.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_addRole] Błąd operacyjny bazy danych: {str(op_err)}")
            self.roleAdditionFailed.emit("Błąd operacyjny bazy danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_addRole] Błąd bazy danych: {str(db_err)}")
            self.roleAdditionFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_addRole] Błąd klucza w danych: {str(ke)}")
            self.roleAdditionFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_addRole] Błąd przetwarzania danych: {str(te)}")
            self.roleAdditionFailed.emit("Błąd przetwarzania danych.")


 # -------------------------------------------------------------------------

    @Slot(int, str)
    def updateRole(self, insert_role_id, insert_role_name):
        """
        Aktualizuje nazwę roli w systemie.

        :param insert_role_id: ID roli do aktualizacji.
        :param insert_role_name: Nowa nazwa roli.
        """
        print(f"[BridgeRoom_updateRole] Otrzymano dane: RoleID={insert_role_id}, RoleName={insert_role_name}")

        errors = []

        try:
            # Inicjalizacja kontrolerów
            admin_service = AdminService(self.main_controller)
            roles_controller = RolesController(self.main_controller.db_controller)

            # **Sprawdzenie czy insert_role_id istnieje w bazie**
            all_role_ids = admin_service.get_all_role_ids()
            if insert_role_id not in all_role_ids:
                errors.append(f"Rola o ID {insert_role_id} nie istnieje w systemie.")

            # **Pobranie listy ról i walidacja insert_role_name**
            all_role_names = admin_service.get_all_role_names()
            normalized_role_name = insert_role_name.strip().capitalize()  # Konwersja np. "KIEROWNIK" → "Kierownik"

            if normalized_role_name in [role.capitalize() for role in all_role_names]:
                errors.append(f"Rola '{insert_role_name}' już istnieje w systemie.")

            # **Jeśli są błędy, emitujemy je i przerywamy działanie**
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_updateRole] Błędy walidacji:\n{error_message}")
                self.roleUpdateFailed.emit(error_message)
                return

            # **Pobranie aktualnych danych roli**
            current_role_data = roles_controller.get_role_by_id(insert_role_id)
            if not current_role_data:
                self.roleUpdateFailed.emit(f"Rola o ID {insert_role_id} nie została znaleziona.")
                return

            # **Sprawdzenie czy istnieją zmiany**
            update_data = {}
            if current_role_data.get("role_name") != normalized_role_name:
                update_data["role_name"] = normalized_role_name

            if not update_data:
                self.roleUpdateFailed.emit("Brak zmian w danych do aktualizacji.")
                return

            # **Wywołanie metody aktualizacji**
            success = roles_controller.update_role(insert_role_id, insert_role_name)

            if success:
                print(f"[BridgeRoom_updateRole] Rola '{normalized_role_name}' została zaktualizowana pomyślnie.")
                self.roleUpdatedSuccessfully.emit()
            else:
                print("[BridgeRoom_updateRole] Nie udało się zaktualizować roli.")
                self.roleUpdateFailed.emit("Nie udało się zaktualizować roli.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_updateRole] Błąd operacyjny bazy danych: {str(op_err)}")
            self.roleUpdateFailed.emit("Błąd operacyjny bazy danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_updateRole] Błąd bazy danych: {str(db_err)}")
            self.roleUpdateFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_updateRole] Błąd klucza w danych: {str(ke)}")
            self.roleUpdateFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_updateRole] Błąd przetwarzania danych: {str(te)}")
            self.roleUpdateFailed.emit("Błąd przetwarzania danych.")

 # -------------------------------------------------------------------------

    @Slot(int)
    def deleteRole(self, insert_role_id):
        """
        Usuwa rolę z systemu po zweryfikowaniu poprawności danych.

        :param insert_role_id: ID roli do usunięcia.
        """
        print(f"[BridgeRoom_deleteRole] Otrzymano żądanie usunięcia roli o ID: {insert_role_id}")

        try:
            # Inicjalizacja kontrolerów
            admin_service = AdminService(self.main_controller)
            roles_controller = RolesController(self.main_controller.db_controller)

            # **Pobranie wszystkich role_id z bazy**
            all_role_ids = admin_service.get_all_role_ids()

            # **Sprawdzenie, czy `insert_role_id` istnieje w bazie**
            if insert_role_id not in all_role_ids:
                msg = f"Rola o ID ({insert_role_id}) nie istnieje w bazie."
                print(f"[BridgeRoom_deleteRole] {msg}")
                self.roleDeletionFailed.emit(msg)
                return

            # **Pobranie wszystkich przypisań roli do użytkowników**
            role_user_assignments = admin_service.get_all_role_user_ids()

            # **Sprawdzenie, czy `insert_role_id` jest przypisane do użytkowników**
            assigned_users = [entry["user_id"] for entry in role_user_assignments if entry["role_id"] == insert_role_id]
            if assigned_users:
                msg = f"Nie można usunąć roli o ID ({insert_role_id}), ponieważ jest przypisana do użytkowników o user_id: {', '.join(map(str, assigned_users))}."
                print(f"[BridgeRoom_deleteRole] {msg}")
                self.roleDeletionFailed.emit(msg)
                return

            # **Próba usunięcia roli**
            success = roles_controller.delete_role_by_id(insert_role_id)

            if success:
                print(f"[BridgeRoom_deleteRole] Rola o ID {insert_role_id} została usunięta.")
                self.roleDeletedSuccessfully.emit()
            else:
                print("[BridgeRoom_deleteRole] Nie udało się usunąć roli.")
                self.roleDeletionFailed.emit("Nie udało się usunąć roli.")

        except ValueError as ve:
            print(f"[BridgeRoom_deleteRole] Błąd wartości: {str(ve)}")
            self.roleDeletionFailed.emit(str(ve))

        except RuntimeError as rue:
            print(f"[BridgeRoom_deleteRole] Błąd bazy danych: {str(rue)}")
            self.roleDeletionFailed.emit("Błąd systemu podczas usuwania roli.")

        except KeyError as ke:
            print(f"[BridgeRoom_deleteRole] Błąd klucza w danych: {str(ke)}")
            self.roleDeletionFailed.emit("Błąd w strukturze danych.")
