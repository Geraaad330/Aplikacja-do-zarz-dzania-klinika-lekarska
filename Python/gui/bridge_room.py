import sqlite3
import re
from datetime import datetime, timedelta
from PySide6.QtCore import QObject, Signal, Slot # pylint: disable=E0611
from services.room_service import RoomService
from controllers.users_accounts_controller import UsersAccountsController
from controllers.rooms_controller import RoomsController
from controllers.room_types_controller import RoomTypesController
from controllers.room_reservations_controller import RoomReservationsController
from controllers.appointments_controller import AppointmentsController
from controllers.assigned_patients_controller import AssignedPatientsController
from controllers.internal_meetings_controller import InternalMeetingsController
from controllers.meeting_participants_controller import MeetingParticipantsController
from controllers.employees_controller import EmployeesController



class BridgeRoom(QObject):
    roomTypesListChanged = Signal(list)
    roomListChanged = Signal(list)
    roomReservationsListChanged = Signal(list)
    roomErrorOccurred = Signal(str)
    roomAddedSuccessfully = Signal()
    roomAdditionFailed = Signal(str)
    roomUpdatedSuccessfully = Signal()
    roomUpdateFailed = Signal(str)
    roomDeletedSuccessfully = Signal()
    roomDeletionFailed = Signal(str)
    roomTypeAddedSuccessfully = Signal()
    roomTypeAdditionFailed = Signal(str)
    roomTypeUpdatedSuccessfully = Signal()
    roomTypeUpdateFailed = Signal(str)
    roomTypeDeletionFailed = Signal(str)
    roomTypeDeletedSuccessfully = Signal()
    reservationAddedSuccessfully = Signal()
    reservationAdditionFailed = Signal(str)
    reservationUpdatedSuccessfully = Signal()
    reservationUpdateFailed = Signal(str)
    reservationDeletedSuccessfully = Signal()
    reservationDeletionFailed = Signal(str)
    appointmentsListChanged = Signal(list)
    meetingTypesListChanged = Signal(list)
    internalMeetingsListChanged = Signal(list)
    appointmentAddedSuccessfully = Signal()
    appointmentAdditionFailed = Signal(str)
    appointmentUpdatedSuccessfully = Signal()
    appointmentUpdateFailed = Signal(str)
    appointmentDeletedSuccessfully = Signal()
    appointmentDeletionFailed = Signal(str)
    internalMeetingAddedSuccessfully = Signal()
    internalMeetingAdditionFailed = Signal(str)
    internalMeetingUpdatedSuccessfully = Signal()
    internalMeetingUpdateFailed = Signal(str)
    internalMeetingDeletedSuccessfully = Signal()
    internalMeetingDeletionFailed = Signal(str)
    internalMeetingParticipantAddedSuccessfully = Signal()
    internalMeetingParticipantAdditionFailed = Signal(str)
    internalMeetingParticipantUpdatedSuccessfully = Signal()
    internalMeetingParticipantUpdateFailed = Signal(str)
    participantDeletedSuccessfully = Signal()
    participantDeletionFailed = Signal(str)
    meetingParticipantsListChanged = Signal(list)



    def __init__(self, main_controller, parent=None):
        try:
            super().__init__(parent)
            print("bridgeRoom initialized")  # Debugging
            self.main_controller = main_controller
            self._logged_in_user_id = None
            self._room_types_list = []
            self._rooms_list = []  # Przechowywana lista pokoi
            self._room_reservations_list = [] 
            self._appointments_list = []
            self._meeting_types_list = []
            self._internal_meetings_list = []
            self._meeting_participants_list = []
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
    def updateRoomTypesList(self):
        """
        Pobiera listę typów pokoi i emituje sygnał do QML.
        """
        try:
            # Pobranie danych z serwisu pokoi
            room_service = RoomService(self.main_controller)
            room_types_list = room_service.get_room_types_table()

            # Debugowanie pobranych danych
            # print(f"[BridgeRoom_updateRoomTypesList] Pobranie danych typów pokoi: {room_types_list}")

            # Aktualizacja listy typów pokoi
            self._room_types_list = room_types_list

            # Emitowanie sygnału z listą typów pokoi
            self.roomTypesListChanged.emit(self._room_types_list)

        except KeyError as ke:
            print(f"[BridgeRoom_updateRoomTypesList] Klucz nie znaleziony w danych typu pokoju: {ke}")
            self.roomTypesListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except ValueError as ve:
            print(f"[BridgeRoom_updateRoomTypesList] Błąd w wartościach danych typu pokoju: {ve}")
            self.roomTypesListChanged.emit([])  # Emituj pustą listę w przypadku błędu

    @Slot(result=list)
    def getRoomTypesList(self):
        """
        Zwraca listę typów pokoi.
        """
        return self._room_types_list

 # -------------------------------------------------------------------------

    @Slot()
    def updateRoomsList(self):
        """
        Pobiera listę pokoi wraz z typami i emituje sygnał do QML.
        """
        try:
            # Pobranie danych z serwisu pokoi
            room_service = RoomService(self.main_controller)
            rooms_list = room_service.get_rooms_with_types()

            # Debugowanie pobranych danych
            # print(f"[BridgeRoom_updateRoomsList] Pobranie danych pokoi: {rooms_list}")

            # Aktualizacja listy pokoi
            self._rooms_list = rooms_list

            # Emitowanie sygnału z listą pokoi
            self.roomListChanged.emit(self._rooms_list)

        except KeyError as ke:
            print(f"[BridgeRoom_updateRoomsList] Klucz nie znaleziony w danych pokoju: {ke}")
            self.roomListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except ValueError as ve:
            print(f"[BridgeRoom_updateRoomsList] Błąd w wartościach danych pokoju: {ve}")
            self.roomListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except RuntimeError as rue:
            print(f"[BridgeRoom_updateRoomsList] Błąd bazy danych: {rue}")
            self.roomListChanged.emit([])  # Emituj pustą listę w przypadku błędu

    @Slot(result=list)
    def getRoomsList(self):
        """
        Zwraca listę pokoi.
        """
        return self._rooms_list
    
 # -------------------------------------------------------------------------


    @Slot()
    def updateRoomReservationsList(self):
        """
        Pobiera listę rezerwacji pokoi wraz ze szczegółami i emituje sygnał do QML.
        """
        try:
            # Pobranie danych rezerwacji z serwisu pokoi
            room_service = RoomService(self.main_controller)
            reservations_list = room_service.get_room_reservations_with_detailed_rooms()

            # Debugowanie pobranych danych
            # print(f"[BridgeRoom_updateRoomReservationsList] Pobranie danych rezerwacji pokoi: {reservations_list}")

            # Aktualizacja listy rezerwacji
            self._room_reservations_list = reservations_list

            # Emitowanie sygnału z listą rezerwacji pokoi
            self.roomReservationsListChanged.emit(self._room_reservations_list)

        except KeyError as ke:
            print(f"[BridgeRoom_updateRoomReservationsList] Klucz nie znaleziony w danych rezerwacji pokoju: {ke}")
            self.roomReservationsListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except ValueError as ve:
            print(f"[BridgeRoom_updateRoomReservationsList] Błąd w wartościach danych rezerwacji pokoju: {ve}")
            self.roomReservationsListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except RuntimeError as rue:
            print(f"[BridgeRoom_updateRoomReservationsList] Błąd bazy danych: {rue}")
            self.roomReservationsListChanged.emit([])  # Emituj pustą listę w przypadku błędu

    @Slot(result=list)
    def getRoomReservationsList(self):
        """
        Zwraca listę rezerwacji pokoi.
        """
        return self._room_reservations_list


 # -------------------------------------------------------------------------

    @Slot(str)
    def checkRoomCrudAccess(self, view_name):
        """
        Sprawdza, czy zalogowany użytkownik ma dostęp do widoku RoomsCRUD.qml.
        Jeśli nie, emituje sygnał o błędzie.
        """
        if self._logged_in_user_id is None:
            print("[BridgeRoom_checkRoomCrudAccess] Brak zalogowanego użytkownika.")
            self.roomErrorOccurred.emit("Brak zalogowanego użytkownika.")
            return

        try:
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
            role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)
            print(f"DEBUG: Pobranie role_id dla użytkownika {self._logged_in_user_id} -> role_id: {role_id}")

            # Sprawdzamy dostęp tylko dla widoku RoomsCRUD.qml
            if view_name == "RoomsCRUD.qml":
                # Zestaw ról blokujących dostęp do widoku RoomsCRUD.qml
                blocked_roles = [3, 4, 5, 6, 7, 8, 11]
                error_message = "Brak uprawnień do zarządzania pokojami."
                if role_id in blocked_roles:
                    print(f"[BridgeRoom_checkRoomCrudAccess] {error_message}")
                    self.roomErrorOccurred.emit(error_message)
                    return

            print(f"[BridgeRoom_checkRoomCrudAccess] Użytkownik ma dostęp do {view_name}.")

        except AttributeError as ae:
            print(f"[BridgeRoom_checkRoomCrudAccess] Błąd atrybutu: {str(ae)}")
            self.roomErrorOccurred.emit("Błąd dostępu do danych użytkownika.")
        except KeyError as ke:
            print(f"[BridgeRoom_checkRoomCrudAccess] Błąd klucza: {str(ke)}")
            self.roomErrorOccurred.emit("Błąd w strukturze danych użytkownika.")
        except TypeError as te:
            print(f"[BridgeRoom_checkRoomCrudAccess] Błąd typu danych: {str(te)}")
            self.roomErrorOccurred.emit("Błąd przetwarzania danych użytkownika.")

 # -------------------------------------------------------------------------

    @Slot(str, str, str)
    def addRoom(self, insert_room_number, insert_floor_number, insert_room_type_id):
        """
        Dodaje nowy pokój do bazy danych na podstawie danych z QML.
        """
        print(f"[BridgeRoom_addRoom] Odebrano dane: RoomNumber={insert_room_number}, FloorNumber={insert_floor_number}, RoomTypeID={insert_room_type_id}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_addRoom] Brak zalogowanego użytkownika.")
            self.roomAdditionFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []  # Lista błędów walidacyjnych

        try:

            room_controller = RoomsController(self.main_controller.db_controller)

            # Konwersja wartości do odpowiednich typów
            room_number = int(insert_room_number)
            floor_number = int(insert_floor_number)
            room_type_id = int(insert_room_type_id)
        except ValueError:
            errors.append("Numer pokoju, numer piętra i ID typu pokoju muszą być liczbami całkowitymi.")

        try:
            # Pobranie wszystkich numerów pokoi
            room_service = RoomService(self.main_controller)
            all_room_numbers = room_service.get_all_room_numbers()

            # Sprawdzenie czy numer pokoju istnieje w bazie
            if room_number in all_room_numbers:
                errors.append(f"Pokój o numerze {room_number} już istnieje w bazie.")

            # Sprawdzenie czy podane piętro jest w zakresie 0-3
            valid_floors = [0, 1, 2, 3]
            if floor_number not in valid_floors:
                errors.append(f"Nieprawidłowe piętro: {floor_number}. Dostępne piętra: {valid_floors}")

            # Pobranie wszystkich dostępnych ID typów pokoi
            all_room_type_ids = room_service.get_all_room_type_ids()

            # Sprawdzenie czy podany `room_type_id` istnieje w bazie
            if room_type_id not in all_room_type_ids:
                errors.append(f"Nieprawidłowe ID typu pokoju: {room_type_id}. Dostępne ID: {all_room_type_ids}")

            # Jeśli są błędy, emitujemy je i przerywamy działanie
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_addRoom] Błędy walidacji:\n{error_message}")
                self.roomAdditionFailed.emit(error_message)
                return

            # Dodanie pokoju do bazy
            success = room_controller.add_room_by_ids(room_number, floor_number, room_type_id)

            if success:
                print("[BridgeRoom_addRoom] Pokój został dodany pomyślnie!")
                self.roomAddedSuccessfully.emit()
            else:
                print("[BridgeRoom_addRoom] Nie udało się dodać pokoju do bazy danych.")
                self.roomAdditionFailed.emit("Wystąpił problem podczas dodawania pokoju.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_addRoom] Błąd operacyjny bazy danych: {str(op_err)}")
            self.roomAdditionFailed.emit("Błąd operacyjny bazy danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_addRoom] Błąd bazy danych: {str(db_err)}")
            self.roomAdditionFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_addRoom] Błąd klucza w danych: {str(ke)}")
            self.roomAdditionFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_addRoom] Błąd przetwarzania danych: {str(te)}")
            self.roomAdditionFailed.emit("Błąd przetwarzania danych.")

 # -------------------------------------------------------------------------


    @Slot(str, str, str, str)
    def updateRoom(self, insert_room_id, insert_room_number="", insert_floor_number="", insert_room_type_id=""):
        """
        Aktualizuje pokój w bazie danych na podstawie podanych danych.
        """
        print(f"[BridgeRoom_updateRoom] Odebrano dane do aktualizacji: "
            f"RoomID={insert_room_id}, RoomNumber={insert_room_number}, "
            f"FloorNumber={insert_floor_number}, RoomTypeID={insert_room_type_id}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_updateRoom] Brak zalogowanego użytkownika.")
            self.roomUpdateFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []
        data_to_update = {}

        try:
            room_controller = RoomsController(self.main_controller.db_controller)
            room_service = RoomService(self.main_controller)

            # Konwersja ID pokoju
            try:
                room_id = int(insert_room_id)
            except ValueError:
                errors.append("ID pokoju musi być liczbą całkowitą.")
                raise

            # Pobierz istniejący pokój
            existing_data = room_controller.get_room_by_id(room_id)
            if not isinstance(existing_data, dict):
                self.roomUpdateFailed.emit(f"Błąd: {existing_data}")
                return

            # Aktualizacja numeru pokoju (tylko jeśli podano nową wartość)
            if insert_room_number.strip():
                try:
                    new_room_number = int(insert_room_number)
                    if new_room_number != existing_data["room_number"]:
                        if new_room_number in room_service.get_all_room_numbers():
                            errors.append(f"Pokój {new_room_number} już istnieje!")
                        else:
                            data_to_update["room_number"] = new_room_number
                except ValueError:
                    errors.append("Nieprawidłowy format numeru pokoju")

            # Aktualizacja piętra (tylko jeśli podano nową wartość)
            if insert_floor_number.strip():
                try:
                    new_floor = int(insert_floor_number)
                    valid_floors = [0, 1, 2, 3]
                    if new_floor not in valid_floors:
                        errors.append(f"Dozwolone piętra: {valid_floors}")
                    elif new_floor != existing_data["floor"]:
                        data_to_update["floor"] = new_floor
                except ValueError:
                    errors.append("Nieprawidłowy format piętra")

            # Aktualizacja typu pokoju (tylko jeśli podano nową wartość)
            if insert_room_type_id.strip():
                try:
                    new_type_id = int(insert_room_type_id)
                    all_type_ids = room_service.get_all_room_type_ids()
                    if new_type_id not in all_type_ids:
                        errors.append("Nieprawidłowy ID typu pokoju")
                    elif new_type_id != existing_data["fk_room_type_id"]:
                        data_to_update["fk_room_type_id"] = new_type_id
                except ValueError:
                    errors.append("Nieprawidłowy format ID typu pokoju")

            # Obsłuż błędy
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_updateRoom] Błędy:\n{error_message}")
                self.roomUpdateFailed.emit(error_message)
                return

            # Jeśli brak zmian
            if not data_to_update:
                print("[BridgeRoom_updateRoom] Brak zmian w danych.")
                self.roomUpdateFailed.emit("Brak zmian w danych.")
                return

            # Wykonaj aktualizację
            print(f"[DEBUG] Finalne dane do aktualizacji: {data_to_update}")
            success = room_controller.update_room_by_ids(room_id, data_to_update)

            if success:
                print("[BridgeRoom_updateRoom] Aktualizacja udana!")
                self.roomUpdatedSuccessfully.emit()
            else:
                print("[BridgeRoom_updateRoom] Aktualizacja nieudana.")
                self.roomUpdateFailed.emit("Błąd podczas aktualizacji.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_updateRoom] Błąd operacyjny bazy danych: {str(op_err)}")
            self.roomUpdateFailed.emit("Błąd operacyjny bazy danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_updateRoom] Błąd bazy danych: {str(db_err)}")
            self.roomUpdateFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_updateRoom] Błąd klucza w danych: {str(ke)}")
            self.roomUpdateFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_updateRoom] Błąd przetwarzania danych: {str(te)}")
            self.roomUpdateFailed.emit("Błąd przetwarzania danych.")

 # -------------------------------------------------------------------------

    @Slot(int)
    def deleteRoom(self, insert_room_id):
        """
        Usuwa pokój z bazy danych na podstawie podanego `room_id`.
        """
        print(f"[BridgeRoom_deleteRoom] Otrzymano żądanie usunięcia pokoju o ID: {insert_room_id}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_deleteRoom] Brak zalogowanego użytkownika.")
            self.roomDeletionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            room_controller = RoomsController(self.main_controller.db_controller)
            room_service = RoomService(self.main_controller)

            # Pobranie wszystkich `room_id` z bazy
            all_room_ids = room_service.get_all_room_ids()

            # Sprawdzenie, czy podany `insert_room_id` istnieje w bazie
            if insert_room_id not in all_room_ids:
                msg = f"Pokój o ID ({insert_room_id}) nie istnieje w bazie."
                print(f"[BridgeRoom_deleteRoom] {msg}")
                self.roomDeletionFailed.emit(msg)
                return

            # Pobranie wszystkich rezerwacji pokoi
            all_room_reservations = room_service.get_all_room_reservations()

            # Sprawdzenie, czy pokój jest powiązany z jakąkolwiek rezerwacją
            reservations_with_room = [
                reservation["reservation_id"]
                for reservation in all_room_reservations
                if reservation["fk_room_id"] == insert_room_id
            ]

            if reservations_with_room:
                reservations_str = ", ".join(map(str, reservations_with_room))
                msg = f"Nie można usunąć pokoju o ID ({insert_room_id}), ponieważ jest przypisany do rezerwacji o ID: {reservations_str}."
                print(f"[BridgeRoom_deleteRoom] {msg}")
                self.roomDeletionFailed.emit(msg)
                return

            # Próba usunięcia pokoju
            success = room_controller.delete_room(insert_room_id)

            if success:
                # print(f"[BridgeRoom_deleteRoom] Pokój o ID {insert_room_id} został pomyślnie usunięty.")
                self.roomDeletedSuccessfully.emit()
            else:
                print(f"[BridgeRoom_deleteRoom] Usunięcie pokoju o ID {insert_room_id} nie powiodło się.")
                self.roomDeletionFailed.emit("Wystąpił problem podczas usuwania pokoju.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_deleteRoom] Błąd operacyjny bazy danych: {str(op_err)}")
            self.roomDeletionFailed.emit("Błąd operacyjny bazy danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_deleteRoom] Błąd bazy danych: {str(db_err)}")
            self.roomDeletionFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_deleteRoom] Błąd klucza w danych: {str(ke)}")
            self.roomDeletionFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_deleteRoom] Błąd przetwarzania danych: {str(te)}")
            self.roomDeletionFailed.emit("Błąd przetwarzania danych.")


 # -------------------------------------------------------------------------

    @Slot(str)
    def addRoomType(self, insert_room_type):
        """
        Dodaje nowy typ pokoju do bazy danych na podstawie podanej nazwy.
        """
        print(f"[BridgeRoom_addRoomType] Odebrano dane: RoomType={insert_room_type}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_addRoomType] Brak zalogowanego użytkownika.")
            self.roomTypeAdditionFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []  # Lista błędów walidacyjnych

        try:
            # Pobranie istniejących typów pokoi
            room_service = RoomService(self.main_controller)
            all_room_types = room_service.get_all_room_types()

            # Normalizacja wielkości liter dla porównania (ignorowanie wielkości liter)
            normalized_room_types = [room_type.lower() for room_type in all_room_types]
            normalized_insert_room_type = insert_room_type.strip().lower()

            # Sprawdzenie, czy typ pokoju już istnieje
            if normalized_insert_room_type in normalized_room_types:
                errors.append(f"Typ pokoju '{insert_room_type}' już istnieje w bazie.")

            # Jeśli są błędy, emitujemy je i kończymy wykonanie
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_addRoomType] Błędy walidacji:\n{error_message}")
                self.roomTypeAdditionFailed.emit(error_message)
                return

            # Wywołanie metody dodającej typ pokoju w kontrolerze
            room_types_controller = RoomTypesController(self.main_controller.db_controller)
            success = room_types_controller.add_room_type(insert_room_type.strip())

            if success:
                print("[BridgeRoom_addRoomType] Typ pokoju został dodany pomyślnie!")
                self.roomTypeAddedSuccessfully.emit()
            else:
                print("[BridgeRoom_addRoomType] Nie udało się dodać typu pokoju do bazy danych.")
                self.roomTypeAdditionFailed.emit("Wystąpił problem podczas dodawania typu pokoju.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_addRoomType] Błąd operacyjny bazy danych: {str(op_err)}")
            self.roomTypeAdditionFailed.emit("Błąd operacyjny bazy danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_addRoomType] Błąd bazy danych: {str(db_err)}")
            self.roomTypeAdditionFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_addRoomType] Błąd klucza w danych: {str(ke)}")
            self.roomTypeAdditionFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_addRoomType] Błąd przetwarzania danych: {str(te)}")
            self.roomTypeAdditionFailed.emit("Błąd przetwarzania danych.")


 # -------------------------------------------------------------------------

    @Slot(str, str)
    def updateRoomType(self, insert_room_type_id, insert_room_type):
        """
        Aktualizuje typ pokoju w bazie danych na podstawie podanych danych.

        :param insert_room_type_id: ID typu pokoju do aktualizacji.
        :param insert_room_type: Nowa nazwa typu pokoju.
        """
        print(f"[BridgeRoom_updateRoomType] Odebrano dane do aktualizacji: RoomTypeID={insert_room_type_id}, RoomType={insert_room_type}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_updateRoomType] Brak zalogowanego użytkownika.")
            self.roomTypeUpdateFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []  # Lista błędów walidacyjnych

        try:
            room_service = RoomService(self.main_controller)
            room_types_controller = RoomTypesController(self.main_controller.db_controller)

            # Konwersja wartości do int
            try:
                room_type_id = int(insert_room_type_id)
            except ValueError:
                errors.append("ID typu pokoju musi być liczbą całkowitą.")

            # Pobranie wszystkich dostępnych ID typów pokoi
            all_room_type_ids = room_service.get_all_room_type_ids()

            # Sprawdzenie czy podany room_type_id istnieje w bazie
            if room_type_id not in all_room_type_ids:
                errors.append(f"Nieprawidłowe ID typu pokoju: {room_type_id}. Dostępne ID: {all_room_type_ids}")

            # Pobranie wszystkich istniejących typów pokoi
            all_room_types = room_service.get_all_room_types()

            # Normalizacja wielkości liter dla porównania (ignorowanie wielkości liter)
            normalized_room_types = [room_type.lower() for room_type in all_room_types]
            normalized_insert_room_type = insert_room_type.strip().lower()

            # Sprawdzenie, czy podana nazwa już istnieje
            if normalized_insert_room_type in normalized_room_types:
                errors.append(f"Typ pokoju '{insert_room_type}' już istnieje w bazie.")

            # Jeśli są błędy, emitujemy je i kończymy wykonanie
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_updateRoomType] Błędy walidacji:\n{error_message}")
                self.roomTypeUpdateFailed.emit(error_message)
                return

            # Wywołanie metody aktualizującej typ pokoju w kontrolerze
            success = room_types_controller.update_room_type(room_type_id, insert_room_type.strip())

            if success:
                print("[BridgeRoom_updateRoomType] Typ pokoju został pomyślnie zaktualizowany!")
                self.roomTypeUpdatedSuccessfully.emit()
            else:
                print("[BridgeRoom_updateRoomType] Nie udało się zaktualizować typu pokoju.")
                self.roomTypeUpdateFailed.emit("Wystąpił problem podczas aktualizacji typu pokoju.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_updateRoomType] Błąd operacyjny bazy danych: {str(op_err)}")
            self.roomTypeUpdateFailed.emit("Błąd operacyjny bazy danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_updateRoomType] Błąd bazy danych: {str(db_err)}")
            self.roomTypeUpdateFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_updateRoomType] Błąd klucza w danych: {str(ke)}")
            self.roomTypeUpdateFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_updateRoomType] Błąd przetwarzania danych: {str(te)}")
            self.roomTypeUpdateFailed.emit("Błąd przetwarzania danych.")


    # -------------------------------------------------------------------------

    @Slot(str)
    def deleteRoomType(self, insert_room_type_id):
        """
        Usuwa typ pokoju z bazy danych na podstawie `room_type_id`.
        """
        print(f"[BridgeRoom_deleteRoomType] Otrzymano żądanie usunięcia typu pokoju o ID: {insert_room_type_id}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_deleteRoomType] Brak zalogowanego użytkownika.")
            self.roomTypeDeletionFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []  # Lista błędów walidacyjnych

        try:
            room_service = RoomService(self.main_controller)
            room_types_controller = RoomTypesController(self.main_controller.db_controller)

            # Konwersja wartości do int
            try:
                room_type_id = int(insert_room_type_id)
            except ValueError:
                errors.append("ID typu pokoju musi być liczbą całkowitą.")

            # Pobranie wszystkich dostępnych ID typów pokoi
            all_room_type_ids = room_service.get_all_room_type_ids()

            # Sprawdzenie, czy podany `room_type_id` istnieje w bazie
            if room_type_id not in all_room_type_ids:
                errors.append(f"Nieprawidłowe ID typu pokoju: {room_type_id}. Dostępne ID: {all_room_type_ids}")

            # Jeśli są błędy, emitujemy je i kończymy wykonanie
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_deleteRoomType] Błędy walidacji:\n{error_message}")
                self.roomTypeDeletionFailed.emit(error_message)
                return

            # Wywołanie metody usuwania typu pokoju w kontrolerze
            success = room_types_controller.delete_room_type(room_type_id)

            if success:
                print(f"[BridgeRoom_deleteRoomType] Typ pokoju o ID {room_type_id} został pomyślnie usunięty!")
                self.roomTypeDeletedSuccessfully.emit()
            else:
                print(f"[BridgeRoom_deleteRoomType] Usunięcie typu pokoju o ID {room_type_id} nie powiodło się.")
                self.roomTypeDeletionFailed.emit("Wystąpił problem podczas usuwania typu pokoju.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_deleteRoomType] Błąd operacyjny bazy danych: {str(op_err)}")
            self.roomTypeDeletionFailed.emit("Błąd operacyjny bazy danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_deleteRoomType] Błąd bazy danych: {str(db_err)}")
            self.roomTypeDeletionFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_deleteRoomType] Błąd klucza w danych: {str(ke)}")
            self.roomTypeDeletionFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_deleteRoomType] Błąd przetwarzania danych: {str(te)}")
            self.roomTypeDeletionFailed.emit("Błąd przetwarzania danych.")


    # -------------------------------------------------------------------------

    @Slot(str, str, str)
    def addReservation(self, insert_room_id, reservation_date, reservation_time):
        """
        Dodaje nową rezerwację do bazy danych.

        :param insert_room_id: ID pokoju do rezerwacji.
        :param reservation_date: Data rezerwacji (YYYY-MM-DD).
        :param reservation_time: Przedział czasowy rezerwacji (HH:MM-HH:MM).
        """
        print(f"[BridgeRoom_addReservation] Otrzymano dane: RoomID={insert_room_id}, Date={reservation_date}, Time={reservation_time}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_addReservation] Brak zalogowanego użytkownika.")
            self.reservationAdditionFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []  # Lista błędów walidacyjnych

        try:
            room_service = RoomService(self.main_controller)
            reservation_controller = RoomReservationsController(self.main_controller.db_controller)

            # Konwersja `insert_room_id` do liczby całkowitej
            try:
                room_id = int(insert_room_id)
            except ValueError:
                errors.append("ID pokoju musi być liczbą całkowitą.")

            # Pobranie wszystkich dostępnych `room_id`
            all_room_ids = room_service.get_all_room_ids()

            # Sprawdzenie, czy pokój istnieje w bazie
            if room_id not in all_room_ids:
                errors.append(f"Pokój o ID {room_id} nie istnieje w bazie.")

            # Walidacja formatu `reservation_date` (YYYY-MM-DD)
            date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
            if not date_pattern.match(reservation_date):
                errors.append("Nieprawidłowy format daty. Poprawny format: YYYY-MM-DD.")
            else:
                # Sprawdzenie, czy data nie jest przeszła
                today = datetime.today().date()
                reservation_date_obj = datetime.strptime(reservation_date, "%Y-%m-%d").date()

                if reservation_date_obj < today:
                    errors.append(f"Data rezerwacji {reservation_date} jest w przeszłości. Podaj dzisiejszą lub przyszłą datę.")

            # Walidacja formatu `reservation_time` (HH:MM-HH:MM)
            time_pattern = re.compile(r"^(\d{2}):(\d{2})-(\d{2}):(\d{2})$")
            match = time_pattern.match(reservation_time)
            if not match:
                errors.append("Nieprawidłowy format godziny. Poprawny format: HH:MM-HH:MM.")
            else:
                # Pobranie godzin i minut z przedziału czasowego
                start_hour, start_minute, end_hour, end_minute = map(int, match.groups())

                start_time = timedelta(hours=start_hour, minutes=start_minute)
                end_time = timedelta(hours=end_hour, minutes=end_minute)

                # Sprawdzenie, czy pierwsza godzina jest wcześniejsza niż druga
                if start_time >= end_time:
                    errors.append("Nieprawidłowy przedział czasowy: godzina rozpoczęcia musi być wcześniejsza niż godzina zakończenia.")

            # Pobranie wszystkich istniejących rezerwacji
            all_reservations = room_service.get_all_room_reservations()

            # Sprawdzenie, czy podana kombinacja już istnieje
            for reservation in all_reservations:
                if (reservation["fk_room_id"] == room_id and
                    reservation["reservation_date"] == reservation_date and
                    reservation["reservation_time"] == reservation_time):
                    errors.append(f"Rezerwacja pokoju {room_id} na dzień {reservation_date} w godzinach {reservation_time} już istnieje.")

            # Jeśli są błędy, emitujemy je i przerywamy działanie
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_addReservation] Błędy walidacji:\n{error_message}")
                self.reservationAdditionFailed.emit(error_message)
                return

            # Dodanie rezerwacji do bazy
            success = reservation_controller.add_reservation(room_id, reservation_date, reservation_time)

            if success:
                print("[BridgeRoom_addReservation] Rezerwacja została dodana pomyślnie!")
                self.reservationAddedSuccessfully.emit()
            else:
                print("[BridgeRoom_addReservation] Nie udało się dodać rezerwacji do bazy danych.")
                self.reservationAdditionFailed.emit("Wystąpił problem podczas dodawania rezerwacji.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_addReservation] Błąd operacyjny bazy danych: {str(op_err)}")
            self.reservationAdditionFailed.emit("Błąd operacyjny bazy danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_addReservation] Błąd bazy danych: {str(db_err)}")
            self.reservationAdditionFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_addReservation] Błąd klucza w danych: {str(ke)}")
            self.reservationAdditionFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_addReservation] Błąd przetwarzania danych: {str(te)}")
            self.reservationAdditionFailed.emit("Błąd przetwarzania danych.")



    # -------------------------------------------------------------------------

    @Slot(str, str, str, str)
    def updateReservation(self, insert_reservation_id, insert_room_id="", reservation_date="", reservation_time=""):
        """
        Aktualizuje rezerwację w bazie danych.
        """
        print(f"[BridgeRoom_updateReservation] Otrzymano dane: ReservationID={insert_reservation_id}, "
            f"RoomID={insert_room_id}, Date={reservation_date}, Time={reservation_time}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_updateReservation] Brak zalogowanego użytkownika.")
            self.reservationUpdateFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []
        data_to_update = {}

        try:
            # Konwersja reservation_id (pole wymagane)
            try:
                reservation_id = int(insert_reservation_id)
            except ValueError:
                errors.append("ID rezerwacji musi być liczbą całkowitą.")
                raise  # Przechodzimy do obsługi błędu

            # Dla pól opcjonalnych – jeśli po strip() ciąg jest pusty, traktujemy jako None
            if insert_room_id is not None and insert_room_id.strip() != "":
                try:
                    new_room_id = int(insert_room_id.strip())
                except ValueError:
                    errors.append("Nieprawidłowy format ID pokoju.")
                    new_room_id = None
            else:
                new_room_id = None

            # Inicjalizacja zmiennych dla pól opcjonalnych
            new_reservation_date = None
            new_reservation_time = None

            # Aktualizacja daty (tylko jeśli podano wartość)
            if reservation_date is not None and reservation_date.strip() != "":
                reservation_date = reservation_date.strip()
                date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
                if not date_pattern.match(reservation_date):
                    errors.append("Nieprawidłowy format daty (YYYY-MM-DD).")
                else:
                    reservation_date_obj = datetime.strptime(reservation_date, "%Y-%m-%d").date()
                    today = datetime.today().date()
                    if reservation_date_obj < today:
                        errors.append("Data rezerwacji nie może być z przeszłości.")
                    else:
                        new_reservation_date = reservation_date
            else:
                new_reservation_date = None

            # Aktualizacja czasu (tylko jeśli podano wartość)
            if reservation_time is not None and reservation_time.strip() != "":
                reservation_time = reservation_time.strip()
                time_pattern = re.compile(r"^(\d{2}):(\d{2})-(\d{2}):(\d{2})$")
                match = time_pattern.match(reservation_time)
                if not match:
                    errors.append("Nieprawidłowy format czasu (HH:MM-HH:MM).")
                else:
                    start_h, start_m, end_h, end_m = map(int, match.groups())
                    if not (0 <= start_h <= 23 and 0 <= start_m <= 59 and 0 <= end_h <= 23 and 0 <= end_m <= 59):
                        errors.append("Nieprawidłowe godziny/minuty (zakres 00-23 dla godzin, 00-59 dla minut).")
                    else:
                        start_time = timedelta(hours=start_h, minutes=start_m)
                        end_time = timedelta(hours=end_h, minutes=end_m)
                        if start_time >= end_time:
                            errors.append("Czas rozpoczęcia musi być przed czasem zakończenia.")
                        else:
                            new_reservation_time = reservation_time
            else:
                new_reservation_time = None


            # Jeżeli pojawiły się błędy już przy konwersji, przerywamy
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_updateReservation] Błędy:\n{error_message}")
                self.reservationUpdateFailed.emit(error_message)
                return

            room_service = RoomService(self.main_controller)
            reservation_controller = RoomReservationsController(self.main_controller.db_controller)

            # Sprawdzenie istnienia rezerwacji
            all_reservation_ids = room_service.get_all_reservation_ids()
            if reservation_id not in all_reservation_ids:
                errors.append(f"Rezerwacja o ID {reservation_id} nie istnieje.")
            else:
                existing_reservation = room_service.get_reservation_by_id(reservation_id)
                if not isinstance(existing_reservation, dict):
                    errors.append("Błąd podczas pobierania danych rezerwacji.")

            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_updateReservation] Błędy:\n{error_message}")
                self.reservationUpdateFailed.emit(error_message)
                return

            # Budowanie słownika danych do aktualizacji – tylko dla pól, które zostały podane
            if new_room_id is not None and new_room_id != existing_reservation.get("fk_room_id"):
                if new_room_id not in room_service.get_all_room_ids():
                    errors.append(f"Pokój o ID {new_room_id} nie istnieje.")
                else:
                    data_to_update["fk_room_id"] = new_room_id

            if new_reservation_date is not None and new_reservation_date != existing_reservation.get("reservation_date"):
                data_to_update["reservation_date"] = new_reservation_date

            if new_reservation_time is not None and new_reservation_time != existing_reservation.get("reservation_time"):
                data_to_update["reservation_time"] = new_reservation_time

            # Sprawdź kolizje rezerwacji, jeśli podano nowe dane lub część z nich
            if data_to_update:
                room_id = data_to_update.get("fk_room_id", existing_reservation.get("fk_room_id"))
                date = data_to_update.get("reservation_date", existing_reservation.get("reservation_date"))
                time = data_to_update.get("reservation_time", existing_reservation.get("reservation_time"))
                for reservation in room_service.get_all_room_reservations():
                    if (reservation["reservation_id"] != reservation_id and
                        reservation["fk_room_id"] == room_id and
                        reservation["reservation_date"] == date and
                        reservation["reservation_time"] == time):
                        errors.append("Konflikt z istniejącą rezerwacją.")
                        break

            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_updateReservation] Błędy:\n{error_message}")
                self.reservationUpdateFailed.emit(error_message)
                return

            if not data_to_update:
                print("[BridgeRoom_updateReservation] Brak zmian w danych.")
                self.reservationUpdateFailed.emit("Brak zmian w danych.")
                return

            success = reservation_controller.update_reservation(
                reservation_id,
                **data_to_update
            )

            if success:
                print("[BridgeRoom_updateReservation] Aktualizacja udana!")
                self.reservationUpdatedSuccessfully.emit()
            else:
                print("[BridgeRoom_updateReservation] Aktualizacja nieudana.")
                self.reservationUpdateFailed.emit("Błąd podczas aktualizacji.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_updateReservation] Błąd operacyjny bazy danych: {str(op_err)}")
            self.reservationAdditionFailed.emit("Błąd operacyjny bazy danych.")
        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_updateReservation] Błąd bazy danych: {str(db_err)}")
            self.reservationAdditionFailed.emit("Błąd bazy danych.")
        except KeyError as ke:
            print(f"[BridgeRoom_updateReservation] Błąd klucza w danych: {str(ke)}")
            self.reservationAdditionFailed.emit("Błąd w strukturze danych.")
        except TypeError as te:
            print(f"[BridgeRoom_updateReservation] Błąd przetwarzania danych: {str(te)}")
            self.reservationAdditionFailed.emit("Błąd przetwarzania danych.")




    # -------------------------------------------------------------------------

    @Slot(str)
    def deleteReservation(self, insert_reservation_id):
        """
        Usuwa rezerwację z bazy danych na podstawie `reservation_id`.
        """
        print(f"[BridgeRoom_deleteReservation] Otrzymano żądanie usunięcia rezerwacji o ID: {insert_reservation_id}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_deleteReservation] Brak zalogowanego użytkownika.")
            self.reservationDeletionFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []  # Lista błędów walidacyjnych

        try:
            room_service = RoomService(self.main_controller)
            reservation_controller = RoomReservationsController(self.main_controller.db_controller)

            # Konwersja wartości do int
            try:
                reservation_id = int(insert_reservation_id)
            except ValueError:
                errors.append("ID rezerwacji musi być liczbą całkowitą.")

            # Pobranie wszystkich `reservation_id`
            all_reservation_ids = room_service.get_all_reservation_ids()

            # Sprawdzenie, czy rezerwacja istnieje w bazie
            if reservation_id not in all_reservation_ids:
                errors.append(f"Rezerwacja o ID {reservation_id} nie istnieje w bazie.")

            # Pobranie `fk_reservation_id` z `appointments`
            appointment_reservations = room_service.get_all_appointment_id_reservation_id()
            appointment_ids = [record["appointment_id"] for record in appointment_reservations if record["fk_reservation_id"] == reservation_id]

            # Pobranie `fk_reservation_id` z `internal_meetings`
            meeting_reservations = room_service.get_all_meeting_id_reservation_id()
            meeting_ids = [record["meeting_id"] for record in meeting_reservations if record["fk_reservation_id"] == reservation_id]

            # Sprawdzenie, czy rezerwacja jest powiązana z `appointments` lub `internal_meetings`
            if appointment_ids or meeting_ids:
                if appointment_ids:
                    errors.append(f"Nie można usunąć rezerwacji {reservation_id}, ponieważ jest powiązana z wizytami o ID: {appointment_ids}.")
                if meeting_ids:
                    errors.append(f"Nie można usunąć rezerwacji {reservation_id}, ponieważ jest powiązana ze spotkaniami o ID: {meeting_ids}.")

            # Jeśli są błędy, emitujemy je i kończymy wykonanie
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_deleteReservation] Błędy walidacji:\n{error_message}")
                self.reservationDeletionFailed.emit(error_message)
                return

            # Wywołanie metody usuwającej rezerwację w kontrolerze
            success = reservation_controller.delete_reservation(reservation_id)

            if success:
                print(f"[BridgeRoom_deleteReservation] Rezerwacja o ID {reservation_id} została pomyślnie usunięta!")
                self.reservationDeletedSuccessfully.emit()
            else:
                print(f"[BridgeRoom_deleteReservation] Nie udało się usunąć rezerwacji o ID {reservation_id}.")
                self.reservationDeletionFailed.emit("Wystąpił problem podczas usuwania rezerwacji.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_deleteReservation] Błąd operacyjny bazy danych: {str(op_err)}")
            self.reservationDeletionFailed.emit("Błąd operacyjny bazy danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_deleteReservation] Błąd bazy danych: {str(db_err)}")
            self.reservationDeletionFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_deleteReservation] Błąd klucza w danych: {str(ke)}")
            self.reservationDeletionFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_deleteReservation] Błąd przetwarzania danych: {str(te)}")
            self.reservationDeletionFailed.emit("Błąd przetwarzania danych.")

    # -------------------------------------------------------------------------

    @Slot()
    def updateAppointmentsList(self):
        """
        Pobiera listę wizyt (`appointments`) na podstawie `role_id` i emituje sygnał do QML.
        """
        try:
            # Pobranie roli użytkownika
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
            role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)

            room_service = RoomService(self.main_controller)

            if role_id in [3, 4, 5, 6, 7, 8]:
                # Pobranie `employee_id` na podstawie zalogowanego użytkownika
                employee_id = users_accounts_controller.get_employee_id_by_user_id(self._logged_in_user_id)

                if employee_id is None:
                    print("[BridgeRoom_updateAppointmentsList] Brak przypisanego pracownika dla zalogowanego użytkownika.")
                    self.appointmentsListChanged.emit([])  # Brak uprawnień, zwróć pustą listę
                    return

                # Pobranie sformatowanych wizyt dla konkretnego pracownika
                appointments_list = room_service.table_get_formatted_appointments_for_employee(employee_id)

            elif role_id in [1, 2, 9, 10]:
                # Pobranie wszystkich wizyt
                appointments_list = room_service.table_get_all_appointments()
            else:
                print(f"[BridgeRoom_updateAppointmentsList] Brak dostępu dla role_id: {role_id}")
                self.appointmentsListChanged.emit([])  # Brak uprawnień, zwróć pustą listę
                return

            # Debugowanie pobranych danych
            # print(f"[BridgeRoom_updateAppointmentsList] Pobranie danych wizyt: {appointments_list}")

            # Aktualizacja listy wizyt
            self._appointments_list = appointments_list

            # Emitowanie sygnału z listą wizyt do frontendu
            self.appointmentsListChanged.emit(self._appointments_list)

        except KeyError as ke:
            print(f"[BridgeRoom_updateAppointmentsList] Klucz nie znaleziony w danych wizyt: {ke}")
            self.appointmentsListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except ValueError as ve:
            print(f"[BridgeRoom_updateAppointmentsList] Błąd w wartościach danych wizyt: {ve}")
            self.appointmentsListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except RuntimeError as rue:
            print(f"[BridgeRoom_updateAppointmentsList] Błąd bazy danych: {rue}")
            self.appointmentsListChanged.emit([])  # Emituj pustą listę w przypadku błędu

    @Slot(result=list)
    def getAppointmentsList(self):
        """
        Zwraca listę wizyt.
        """
        return self._appointments_list

    # -------------------------------------------------------------------------

    @Slot()
    def updateMeetingTypesList(self):
        """
        Pobiera listę typów spotkań i emituje sygnał do QML.
        """
        try:
            # Pobranie danych typów spotkań z serwisu pokoi
            room_service = RoomService(self.main_controller)
            meeting_types_list = room_service.table_get_all_meeting_types()

            # Debugowanie pobranych danych
            # print(f"[BridgeRoom_updateMeetingTypesList] Pobranie typów spotkań: {meeting_types_list}")

            # Aktualizacja listy typów spotkań
            self._meeting_types_list = meeting_types_list

            # Emitowanie sygnału z listą typów spotkań
            self.meetingTypesListChanged.emit(self._meeting_types_list)

        except KeyError as ke:
            print(f"[BridgeRoom_updateMeetingTypesList] Klucz nie znaleziony w danych typów spotkań: {ke}")
            self.meetingTypesListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except ValueError as ve:
            print(f"[BridgeRoom_updateMeetingTypesList] Błąd w wartościach danych typów spotkań: {ve}")
            self.meetingTypesListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except RuntimeError as rue:
            print(f"[BridgeRoom_updateMeetingTypesList] Błąd bazy danych: {rue}")
            self.meetingTypesListChanged.emit([])  # Emituj pustą listę w przypadku błędu

    @Slot(result=list)
    def getMeetingTypesList(self):
        """
        Zwraca listę typów spotkań.
        """
        return self._meeting_types_list


    # -------------------------------------------------------------------------

    @Slot()
    def updateInternalMeetingsList(self):
        """
        Pobiera listę spotkań wewnętrznych i emituje sygnał do QML.
        """
        try:
            # Pobranie danych spotkań wewnętrznych z serwisu pokoi
            room_service = RoomService(self.main_controller)
            internal_meetings_list = room_service.table_get_all_internal_meetings()

            # Debugowanie pobranych danych
            # print(f"[BridgeRoom_updateInternalMeetingsList] Pobranie danych spotkań wewnętrznych: {internal_meetings_list}")

            # Aktualizacja listy spotkań wewnętrznych
            self._internal_meetings_list = internal_meetings_list

            # Emitowanie sygnału z listą spotkań wewnętrznych
            self.internalMeetingsListChanged.emit(self._internal_meetings_list)

        except KeyError as ke:
            print(f"[BridgeRoom_updateInternalMeetingsList] Klucz nie znaleziony w danych spotkań: {ke}")
            self.internalMeetingsListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except ValueError as ve:
            print(f"[BridgeRoom_updateInternalMeetingsList] Błąd w wartościach danych spotkań: {ve}")
            self.internalMeetingsListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except RuntimeError as rue:
            print(f"[BridgeRoom_updateInternalMeetingsList] Błąd bazy danych: {rue}")
            self.internalMeetingsListChanged.emit([])  # Emituj pustą listę w przypadku błędu

    @Slot(result=list)
    def getInternalMeetingsList(self):
        """
        Zwraca listę spotkań wewnętrznych.
        """
        return self._internal_meetings_list

    # -------------------------------------------------------------------------

    @Slot(str, str, str, str, str)
    def addAppointment(self, insert_assignment_id, insert_service_id, insert_reservation_id, insert_appointment_status, insert_notes):
        """
        Dodaje nową wizytę do bazy danych po zweryfikowaniu poprawności danych.

        :param insert_assignment_id: ID przypisania pacjenta do pracownika.
        :param insert_service_id: ID usługi.
        :param insert_reservation_id: ID rezerwacji pokoju.
        :param insert_appointment_status: Status wizyty (Zrealizowana, Odwołana, Zaplanowana).
        :param insert_notes: Notatki do wizyty.
        """
        print(f"[BridgeRoom_addAppointment] Otrzymano dane: AssignmentID={insert_assignment_id}, ServiceID={insert_service_id}, ReservationID={insert_reservation_id}, Status={insert_appointment_status}, Notes={insert_notes}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_addAppointment] Brak zalogowanego użytkownika.")
            self.appointmentAdditionFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []  # Lista błędów walidacyjnych

        try:
            # Konwersja ID na int (aby uniknąć błędów)
            try:
                insert_assignment_id = int(insert_assignment_id)
                insert_service_id = int(insert_service_id)
                insert_reservation_id = int(insert_reservation_id)
            except ValueError:
                self.appointmentAdditionFailed.emit("ID przypisania, ID usługi oraz ID rezerwacji muszą być liczbami całkowitymi.")
                return

            room_service = RoomService(self.main_controller)
            appointment_controller = AppointmentsController(self.main_controller.db_controller)
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
            

            # Pobranie roli użytkownika
            role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)

            if role_id in [3, 4, 5, 6, 7, 8]:
                # Pobranie `employee_id`
                employee_id = users_accounts_controller.get_employee_id_by_user_id(self._logged_in_user_id)

                if employee_id is None:
                    errors.append("Brak przypisanego pracownika dla zalogowanego użytkownika.")
                else:
                    # Pobranie listy `assignment_id` przypisanych do pracownika
                    valid_assignment_ids_for_employee = room_service.get_all_assignment_ids_for_employee(employee_id)

                    if not valid_assignment_ids_for_employee:
                        errors.append(f"Brak przypisań pacjentów do pracownika {employee_id}.")
                    elif insert_assignment_id not in valid_assignment_ids_for_employee:
                        errors.append(f"Przypisanie o ID {insert_assignment_id} nie jest przypisane do pracownika {employee_id}. "
                                    f"Dostępne ID przypisań: {valid_assignment_ids_for_employee}")

                    # Pobranie listy `service_id` przypisanych do pracownika
                    valid_service_ids_for_employee = room_service.get_all_service_ids_by_employee(employee_id)

                    if not valid_service_ids_for_employee:
                        errors.append(f"Brak przypisanych usług dla pracownika {employee_id}.")
                    elif insert_service_id not in valid_service_ids_for_employee:
                        errors.append(f"Usługa o ID {insert_service_id} nie jest przypisana do pracownika {employee_id}. "
                                    f"Dostępne ID usług: {valid_service_ids_for_employee}")



            elif role_id in [1, 2, 9, 10]:
                # Pobranie listy `assignment_id`
                all_assignment_ids = room_service.get_all_assignment_ids()
                if insert_assignment_id not in all_assignment_ids:
                    errors.append(f"Przypisanie o ID {insert_assignment_id} nie istnieje w systemie.")
                else:
                    # Pobranie `employee_id` na podstawie `assignment_id`
                    employee_id = room_service.get_all_employee_id_for_assignment(insert_assignment_id)

                    if not employee_id:
                        errors.append(f"Nie znaleziono pracownika przypisanego do assignment_id {insert_assignment_id}.")
                    else:
                        # Pobranie listy `service_id` przypisanych do `employee_id`
                        valid_service_ids_for_employee = room_service.get_all_service_ids_by_employee(employee_id)

                        if not valid_service_ids_for_employee:
                            errors.append(f"Brak przypisanych usług dla pracownika {employee_id}.")
                        elif insert_service_id not in valid_service_ids_for_employee:
                            errors.append(f"Usługa o ID {insert_service_id} nie jest przypisana do pracownika o ID {employee_id}. "
                                        f"Dostępne ID usług: {valid_service_ids_for_employee}")




            # **Nowe sprawdzenie, czy insert_reservation_id istnieje w bazie**
            all_reservation_ids = room_service.get_all_reservation_ids()
            if insert_reservation_id not in all_reservation_ids:
                errors.append(f"Rezerwacja o ID {insert_reservation_id} nie istnieje w bazie.")
            else:
                # Pobranie wszystkich `reservation_id` z `appointments` i sprawdzenie, czy istnieje
                existing_reservation_ids_appointments = room_service.get_all_reservation_ids_from_appointments()
                if insert_reservation_id in existing_reservation_ids_appointments:
                    errors.append(f"Rezerwacja o ID {insert_reservation_id} już istnieje w tabeli wizyty.")

                existing_reservation_ids_meetings = room_service.get_all_reservation_ids_from_internal_meetings()
                if insert_reservation_id in existing_reservation_ids_meetings:
                    errors.append(f"Rezerwacja o ID {insert_reservation_id} już istnieje w tabeli spotkania wewnętrzne.")

            # Pobranie i zmodyfikowanie daty rezerwacji
            modified_appointment_date = room_service.get_reservation_datetime(insert_reservation_id)

            # Walidacja `insert_appointment_status`
            valid_statuses = ["Zrealizowana", "Odwołana", "Zaplanowana"]
            if insert_appointment_status not in valid_statuses:
                errors.append(f"Niepoprawny status wizyty: {insert_appointment_status}. Dozwolone: {', '.join(valid_statuses)}")

            # Jeśli są błędy, emitujemy je i przerywamy działanie
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_addAppointment] Błędy walidacji:\n{error_message}")
                self.appointmentAdditionFailed.emit(error_message)
                return

            # Dodanie wizyty do bazy
            success = appointment_controller.add_appointment(
                insert_assignment_id, 
                insert_service_id, 
                insert_reservation_id, 
                modified_appointment_date, 
                insert_appointment_status, 
                insert_notes
            )

            if success:
                print("[BridgeRoom_addAppointment] Wizyta została dodana pomyślnie!")
                self.appointmentAddedSuccessfully.emit()
            else:
                print("[BridgeRoom_addAppointment] Nie udało się dodać wizyty do bazy danych.")
                self.appointmentAdditionFailed.emit("Wystąpił problem podczas dodawania wizyty.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_addAppointment] Błąd operacyjny bazy danych: {str(op_err)}")
            self.appointmentAdditionFailed.emit("Błąd operacyjny bazy danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_addAppointment] Błąd bazy danych: {str(db_err)}")
            self.appointmentAdditionFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_addAppointment] Błąd klucza w danych: {str(ke)}")
            self.appointmentAdditionFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_addAppointment] Błąd przetwarzania danych: {str(te)}")
            self.appointmentAdditionFailed.emit("Błąd przetwarzania danych.")


    # -------------------------------------------------------------------------


    @Slot(str, str, str, str, str, str)
    def updateAppointment(self, insert_appointment_id, insert_assignment_id=None, insert_service_id=None,
                        insert_reservation_id=None, insert_appointment_status=None, insert_notes=None):
        """
        Aktualizuje wizytę w bazie danych po zweryfikowaniu poprawności danych.
        """
        print(f"[BridgeRoom_updateAppointment] Otrzymano dane: AppointmentID={insert_appointment_id}, "
            f"AssignmentID={insert_assignment_id}, ServiceID={insert_service_id}, ReservationID={insert_reservation_id}, "
            f"Status={insert_appointment_status}, Notes={insert_notes}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_updateAppointment] Brak zalogowanego użytkownika.")
            self.appointmentUpdateFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []

        try:
            try:
                # Konwersja ID na int (pola opcjonalne – jeśli puste, traktujemy jako None)
                insert_appointment_id = int(insert_appointment_id)
                insert_assignment_id = int(insert_assignment_id) if insert_assignment_id is not None and insert_assignment_id.strip() != "" else None
                insert_service_id = int(insert_service_id) if insert_service_id is not None and insert_service_id.strip() != "" else None
                insert_reservation_id = int(insert_reservation_id) if insert_reservation_id is not None and insert_reservation_id.strip() != "" else None
            except ValueError:
                self.appointmentUpdateFailed.emit("ID muszą być liczbami całkowitymi.")
                return

            # Dla tekstowych pól opcjonalnych – jeśli puste po trimowaniu, ustawiamy na None
            if insert_appointment_status is not None:
                insert_appointment_status = insert_appointment_status.strip()
                if insert_appointment_status == "":
                    insert_appointment_status = None
            if insert_notes is not None:
                insert_notes = insert_notes.strip()
                if insert_notes == "":
                    insert_notes = None

            room_service = RoomService(self.main_controller)
            appointment_controller = AppointmentsController(self.main_controller.db_controller)
            users_accounts_controller = UsersAccountsController(self.main_controller.db_controller)
            assigned_patients_controller = AssignedPatientsController(self.main_controller.db_controller)

            # Pobranie roli użytkownika
            role_id = users_accounts_controller.get_role_id_by_user_id(self._logged_in_user_id)

            if role_id in [3, 4, 5, 6, 7, 8]:  # Rola pracownika medycznego
                employee_id = users_accounts_controller.get_employee_id_by_user_id(self._logged_in_user_id)
                valid_assignment_ids_for_employee = room_service.get_all_assignment_ids_for_employee(employee_id)
                valid_appointments = room_service.get_appointment_ids_by_assignment(valid_assignment_ids_for_employee)
                valid_services = room_service.get_all_service_ids_for_employee(employee_id)

                if insert_appointment_id not in valid_appointments:
                    errors.append(
                        f"Użytkownik o ID pracownika {employee_id} może aktualizować tylko przypisane wizyty: {valid_appointments}"
                    )
                if insert_assignment_id is not None and insert_assignment_id not in valid_assignment_ids_for_employee:
                    errors.append(
                        f"Przypisanie o ID {insert_assignment_id} nie istnieje lub nie należy do pracownika {employee_id}. "
                        f"Dostępne ID: {valid_assignment_ids_for_employee}"
                    )
                if insert_service_id is not None and insert_service_id not in valid_services:
                    errors.append(
                        f"Usługa o ID {insert_service_id} nie istnieje lub nie jest dostępna dla pracownika {employee_id}. "
                        f"Dostępne ID: {valid_services}"
                    )

            elif role_id in [1, 2, 9, 10]:
                all_appointment_ids = room_service.get_all_appointment_ids()
                if insert_appointment_id not in all_appointment_ids:
                    errors.append(f"Przypisanie o ID {insert_appointment_id} nie istnieje w systemie.")
                else:
                    assignment_id = appointment_controller.get_assignment_id_by_appointment_id(insert_appointment_id)
                    employee_id = assigned_patients_controller.get_employee_id_by_assignment_id(assignment_id)
                    valid_assignment_ids_for_employee = room_service.get_all_assignment_ids_for_employee(employee_id)
                    valid_appointments = room_service.get_appointment_ids_by_assignment(valid_assignment_ids_for_employee)
                    valid_services = room_service.get_all_service_ids_for_employee(employee_id)
                    if insert_appointment_id not in valid_appointments:
                        errors.append(
                            f"Użytkownik o ID pracownika {employee_id} może aktualizować tylko przypisane wizyty: {valid_appointments}"
                        )
                    if insert_assignment_id is not None and insert_assignment_id not in valid_assignment_ids_for_employee:
                        errors.append(
                            f"Przypisanie o ID {insert_assignment_id} nie istnieje lub nie należy do pracownika {employee_id}. "
                            f"Dostępne ID: {valid_assignment_ids_for_employee}"
                        )
                    if insert_service_id is not None and insert_service_id not in valid_services:
                        errors.append(
                            f"Usługa o ID {insert_service_id} nie istnieje lub nie jest dostępna dla pracownika {employee_id}. "
                            f"Dostępne ID: {valid_services}"
                        )

            # Sprawdzenie rezerwacji
            existing_appointment_reservation_ids = room_service.get_all_reservation_ids_from_appointments()
            if insert_reservation_id is not None and insert_reservation_id in existing_appointment_reservation_ids:
                errors.append(f"Rezerwacja o ID {insert_reservation_id} już istnieje w tabeli wizyt.")
            existing_room_reservation_ids = room_service.get_all_reservation_ids()
            if insert_reservation_id is not None and insert_reservation_id not in existing_room_reservation_ids:
                errors.append(f"Rezerwacja o ID {insert_reservation_id} nie istnieje w tabeli rezerwacje.")

            # Pobranie i ewentualna modyfikacja daty rezerwacji
            modified_appointment_date = room_service.get_reservation_datetime(insert_reservation_id) if insert_reservation_id else None

            # Walidacja statusu wizyty
            valid_statuses = ["Zrealizowana", "Odwołana", "Zaplanowana"]
            if insert_appointment_status is not None:
                if insert_appointment_status not in valid_statuses:
                    errors.append(f"Niepoprawny status wizyty: {insert_appointment_status}. Dozwolone: {', '.join(valid_statuses)}")

            # Pobranie obecnych danych wizyty
            existing_appointment_data = appointment_controller.get_appointment_by_id(insert_appointment_id)
            if not existing_appointment_data:
                errors.append(f"Wizyta o ID {insert_appointment_id} nie istnieje.")
            else:
                required_keys = ["fk_assignment_id", "fk_service_id", "fk_reservation_id", "appointment_status", "notes"]
                for key in required_keys:
                    if key not in existing_appointment_data:
                        errors.append(f"Błąd w strukturze danych: brak klucza `{key}` w istniejących danych wizyty.")

            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_updateAppointment] Błędy walidacji:\n{error_message}")
                self.appointmentUpdateFailed.emit(error_message)
                return

            # Budowanie słownika danych do aktualizacji – tylko dla pól, które użytkownik podał (niepustych)
            update_data = {}
            if insert_assignment_id is not None and insert_assignment_id != existing_appointment_data["fk_assignment_id"]:
                update_data["fk_assignment_id"] = insert_assignment_id
            if insert_service_id is not None and insert_service_id != existing_appointment_data["fk_service_id"]:
                update_data["fk_service_id"] = insert_service_id
            if insert_reservation_id is not None and insert_reservation_id != existing_appointment_data["fk_reservation_id"]:
                update_data["fk_reservation_id"] = insert_reservation_id
            if modified_appointment_date is not None and modified_appointment_date != existing_appointment_data["appointment_date"]:
                update_data["appointment_date"] = modified_appointment_date
            if insert_appointment_status is not None and insert_appointment_status != existing_appointment_data["appointment_status"]:
                update_data["appointment_status"] = insert_appointment_status
            if insert_notes is not None and insert_notes != existing_appointment_data["notes"]:
                update_data["notes"] = insert_notes

            if not update_data:
                print("[BridgeRoom_updateAppointment] Brak zmian w danych do aktualizacji.")
                self.appointmentUpdateFailed.emit("Brak zmian w danych do aktualizacji.")
                return

            success = appointment_controller.update_appointment(
                appointment_id=insert_appointment_id,
                assignment_id=update_data.get("fk_assignment_id"),
                service_id=update_data.get("fk_service_id"),
                reservation_id=update_data.get("fk_reservation_id"),
                appointment_date=update_data.get("appointment_date"),
                appointment_status=update_data.get("appointment_status"),
                notes=update_data.get("notes")
            )

            if success:
                print("[BridgeRoom_updateAppointment] Wizyta została zaktualizowana pomyślnie!")
                self.appointmentUpdatedSuccessfully.emit()
            else:
                print("[BridgeRoom_updateAppointment] Nie dokonano żadnych zmian w bazie danych.")
                self.appointmentUpdateFailed.emit("Nie dokonano żadnych zmian w bazie danych.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_updateAppointment] Błąd operacyjny bazy danych: {str(op_err)}")
            self.appointmentUpdateFailed.emit("Błąd operacyjny bazy danych.")
        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_updateAppointment] Błąd bazy danych: {str(db_err)}")
            self.appointmentUpdateFailed.emit("Błąd bazy danych.")



    # -------------------------------------------------------------------------

    @Slot(int)
    def deleteAppointment(self, insert_appointment_id):
        """
        Usuwa wizytę (appointment_id) z bazy danych po zweryfikowaniu, że nie jest powiązana z diagnozami i receptami.

        :param insert_appointment_id: ID wizyty do usunięcia.
        """
        print(f"[BridgeRoom_deleteAppointment] Otrzymano żądanie usunięcia wizyty o ID: {insert_appointment_id}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_deleteAppointment] Brak zalogowanego użytkownika.")
            self.appointmentDeletionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            room_service = RoomService(self.main_controller)
            appointment_controller = AppointmentsController(self.main_controller.db_controller)

            # Pobranie wszystkich `appointment_id` z bazy
            all_appointment_ids = room_service.get_all_appointment_ids()

            # Sprawdzenie, czy podany `insert_appointment_id` istnieje w bazie
            if insert_appointment_id not in all_appointment_ids:
                msg = f"Wizyta o ID ({insert_appointment_id}) nie istnieje w bazie."
                print(f"[BridgeRoom_deleteAppointment] {msg}")
                self.appointmentDeletionFailed.emit(msg)
                return

            # Pobranie wszystkich `fk_appointment_id` i `diagnosis_id` z tabeli diagnoses
            diagnoses_data = room_service.get_all_appointment_ids_diagnoses_ids_from_diagnoses()
            diagnosis_ids = [entry["diagnosis_id"] for entry in diagnoses_data if entry["fk_appointment_id"] == insert_appointment_id]

            # Sprawdzenie, czy `insert_appointment_id` jest powiązane z diagnozami
            if diagnosis_ids:
                msg = f"Nie można usunąć wizyty o ID {insert_appointment_id}, ponieważ jest przypisana w następujących diagnosis_id: {diagnosis_ids}"
                print(f"[BridgeRoom_deleteAppointment] {msg}")
                self.appointmentDeletionFailed.emit(msg)
                return

            # Pobranie wszystkich `fk_appointment_id` i `prescription_id` z tabeli prescriptions
            prescriptions_data = room_service.get_all_appointment_ids_prescriptions_ids_from_prescriptions()
            prescription_ids = [entry["prescription_id"] for entry in prescriptions_data if entry["fk_appointment_id"] == insert_appointment_id]

            # Sprawdzenie, czy `insert_appointment_id` jest powiązane z receptami
            if prescription_ids:
                msg = f"Nie można usunąć wizyty o ID {insert_appointment_id}, ponieważ jest przypisana w następujących prescriptions_id: {prescription_ids}"
                print(f"[BridgeRoom_deleteAppointment] {msg}")
                self.appointmentDeletionFailed.emit(msg)
                return

            # Próba usunięcia wizyty
            success = appointment_controller.delete_appointment(insert_appointment_id)

            if success:
                print(f"[BridgeRoom_deleteAppointment] Wizyta o ID {insert_appointment_id} została pomyślnie usunięta.")
                self.appointmentDeletedSuccessfully.emit()
            else:
                print(f"[BridgeRoom_deleteAppointment] Nie udało się usunąć wizyty o ID {insert_appointment_id}.")
                self.appointmentDeletionFailed.emit("Nie udało się usunąć wizyty.")

        except ValueError as ve:
            print(f"[BridgeRoom_deleteAppointment] Błąd wartości: {str(ve)}")
            self.appointmentDeletionFailed.emit(str(ve))

        except RuntimeError as rue:
            print(f"[BridgeRoom_deleteAppointment] Błąd bazy danych: {str(rue)}")
            self.appointmentDeletionFailed.emit("Błąd systemu podczas usuwania wizyty.")

        except KeyError as ke:
            print(f"[BridgeRoom_deleteAppointment] Błąd klucza w danych: {str(ke)}")
            self.appointmentDeletionFailed.emit("Błąd w strukturze danych.")



    # -------------------------------------------------------------------------

    @Slot(str, str, str, str)
    def addInternalMeeting(self, insert_meeting_type_id, insert_reservation_id, insert_notes, insert_internal_meeting_status):
        """
        Dodaje nowe spotkanie wewnętrzne do bazy danych po zweryfikowaniu poprawności danych.

        :param insert_meeting_type_id: ID typu spotkania.
        :param insert_reservation_id: ID rezerwacji pokoju.
        :param insert_notes: Notatki do spotkania.
        :param insert_internal_meeting_status: Status spotkania.
        """
        print(f"[BridgeRoom_addInternalMeeting] Otrzymano dane: MeetingTypeID={insert_meeting_type_id}, "
            f"ReservationID={insert_reservation_id}, Status={insert_internal_meeting_status}, Notes={insert_notes}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_addInternalMeeting] Brak zalogowanego użytkownika.")
            self.internalMeetingAdditionFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []  # Lista błędów walidacyjnych

        try:
            # Konwersja ID na int (aby uniknąć błędów)
            try:
                insert_meeting_type_id = int(insert_meeting_type_id)
                insert_reservation_id = int(insert_reservation_id)
            except ValueError:
                self.internalMeetingAdditionFailed.emit("ID typu spotkania oraz ID rezerwacji muszą być liczbami całkowitymi.")
                return

            room_service = RoomService(self.main_controller)
            internal_meetings_controller = InternalMeetingsController(self.main_controller.db_controller)

            # **Sprawdzenie czy `insert_meeting_type_id` istnieje w systemie**
            all_meeting_type_ids = room_service.get_all_meeting_type_ids()
            if insert_meeting_type_id not in all_meeting_type_ids:
                errors.append(f"Typ spotkania o ID {insert_meeting_type_id} nie istnieje w tabeli typy spotkań. Dostępne typy spotkań o ID: {all_meeting_type_ids}")

            # Sprawdzenie czy `insert_reservation_id` już istnieje w tabeli wizyt
            existing_appointment_reservation_ids = room_service.get_all_reservation_ids_from_appointments()
            if insert_reservation_id is not None and insert_reservation_id in existing_appointment_reservation_ids:
                errors.append(f"Rezerwacja o ID {insert_reservation_id} już istnieje w tabeli wizyty.")

            existing_internal_reservation_ids = room_service.get_all_reservation_ids_from_internal_meetings()
            if insert_reservation_id is not None and insert_reservation_id in existing_internal_reservation_ids:
                errors.append(f"Rezerwacja o ID {insert_reservation_id} już istnieje w tabeli spotkania wewnętrzne.")

            existing_room_reservation_ids = room_service.get_all_reservation_ids()
            if insert_reservation_id is not None and insert_reservation_id not in existing_room_reservation_ids:
                errors.append(f"Rezerwacja o ID {insert_reservation_id}  nie istnieje w tabeli rezerwacje.")
    

            # **Pobranie i zmodyfikowanie daty rezerwacji**
            modified_meeting_date = room_service.get_reservation_datetime(insert_reservation_id)

            # **Walidacja `insert_internal_meeting_status` (niewrażliwa na wielkość liter)**
            valid_statuses = ["Zaplanowane", "Zakończone", "Odwołane", "Przełożone", "Oczekujące"]

            # Konwersja wprowadzonego statusu na wersję z małymi literami
            normalized_status = insert_internal_meeting_status.lower()

            # Konwersja dozwolonych statusów na wersję z małymi literami
            valid_statuses_lower = [status.lower() for status in valid_statuses]

            if normalized_status not in valid_statuses_lower:
                errors.append(f"Niepoprawny status spotkania: {insert_internal_meeting_status}. "
                            f"Dozwolone: {', '.join(valid_statuses)}")


            # **Jeśli są błędy, emitujemy je i przerywamy działanie**
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_addInternalMeeting] Błędy walidacji:\n{error_message}")
                self.internalMeetingAdditionFailed.emit(error_message)
                return

            # **Dodanie spotkania do bazy**
            meeting_id = internal_meetings_controller.add_meeting(
                fk_meeting_type_id=insert_meeting_type_id,
                fk_reservation_id=insert_reservation_id,
                meeting_date=modified_meeting_date,
                notes=insert_notes,
                internal_meeting_status=insert_internal_meeting_status
            )

            if meeting_id:
                print(f"[BridgeRoom_addInternalMeeting] Spotkanie zostało dodane pomyślnie! ID: {meeting_id}")
                self.internalMeetingAddedSuccessfully.emit()
            else:
                print("[BridgeRoom_addInternalMeeting] Nie udało się dodać spotkania do bazy danych.")
                self.internalMeetingAdditionFailed.emit("Wystąpił problem podczas dodawania spotkania.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_addInternalMeeting] Błąd operacyjny bazy danych: {str(op_err)}")
            self.internalMeetingAdditionFailed.emit("Błąd operacyjny bazy danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_addInternalMeeting] Błąd bazy danych: {str(db_err)}")
            self.internalMeetingAdditionFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_addInternalMeeting] Błąd klucza w danych: {str(ke)}")
            self.internalMeetingAdditionFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_addInternalMeeting] Błąd przetwarzania danych: {str(te)}")
            self.internalMeetingAdditionFailed.emit("Błąd przetwarzania danych.")



    # -------------------------------------------------------------------------

    @Slot(str, str, str, str, str)
    def updateInternalMeeting(
        self, 
        insert_meeting_id, 
        insert_meeting_type_id=None, 
        insert_reservation_id=None, 
        insert_notes=None, 
        insert_internal_meeting_status=None
    ):
        """
        Aktualizuje spotkanie wewnętrzne w bazie danych po zweryfikowaniu poprawności danych.

        :param insert_meeting_id: ID spotkania do aktualizacji (wymagane).
        :param insert_meeting_type_id: (Opcjonalne) Nowe ID typu spotkania.
        :param insert_reservation_id: (Opcjonalne) Nowe ID rezerwacji pokoju.
        :param insert_notes: (Opcjonalne) Nowe notatki do spotkania.
        :param insert_internal_meeting_status: (Opcjonalne) Nowy status spotkania.
        """
        print(f"[BridgeRoom_updateInternalMeeting] Otrzymano dane: MeetingID={insert_meeting_id}, "
            f"MeetingTypeID={insert_meeting_type_id}, ReservationID={insert_reservation_id}, "
            f"Status={insert_internal_meeting_status}, Notes={insert_notes}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_updateInternalMeeting] Brak zalogowanego użytkownika.")
            self.internalMeetingUpdateFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []  # Lista błędów walidacyjnych

        try:
            # **Konwersja ID na int tylko jeśli wartości są podane**
            try:
                insert_meeting_id = int(insert_meeting_id)  # ID spotkania jest wymagane
                insert_meeting_type_id = int(insert_meeting_type_id) if insert_meeting_type_id and insert_meeting_type_id.strip() else None
                insert_reservation_id = int(insert_reservation_id) if insert_reservation_id and insert_reservation_id.strip() else None
            except ValueError:
                self.internalMeetingUpdateFailed.emit("ID spotkania, ID typu spotkania oraz ID rezerwacji muszą być liczbami całkowitymi.")
                return

            # **Inicjalizacja kontrolerów**
            room_service = RoomService(self.main_controller)
            internal_meetings_controller = InternalMeetingsController(self.main_controller.db_controller)

            # **Sprawdzenie czy `insert_meeting_id` istnieje**
            all_meeting_ids = room_service.get_all_meeting_ids()
            if insert_meeting_id not in all_meeting_ids:
                errors.append(f"Spotkanie o ID {insert_meeting_id} nie istnieje w systemie.")

            # **Sprawdzenie czy `insert_meeting_type_id` istnieje (jeśli podano)**
            if insert_meeting_type_id is not None:
                all_meeting_type_ids = room_service.get_all_room_type_ids()
                if insert_meeting_type_id not in all_meeting_type_ids:
                    errors.append(f"Typ spotkania o ID {insert_meeting_type_id} nie istnieje w systemie.")

            # **Sprawdzenie czy `insert_reservation_id` istnieje i czy nie jest zajęte (jeśli podano)**
            if insert_reservation_id is not None:
                existing_appointment_reservation_ids = room_service.get_all_reservation_ids_from_appointments()
                if insert_reservation_id in existing_appointment_reservation_ids:
                    errors.append(f"Rezerwacja o ID {insert_reservation_id} już istnieje w tabeli wizyty.")

                existing_internal_reservation_ids = room_service.get_all_reservation_ids_from_internal_meetings()
                if insert_reservation_id in existing_internal_reservation_ids:
                    errors.append(f"Rezerwacja o ID {insert_reservation_id} już istnieje w tabeli spotkań wewnętrznych.")

                existing_room_reservation_ids = room_service.get_all_reservation_ids()
                if insert_reservation_id not in existing_room_reservation_ids:
                    errors.append(f"Rezerwacja o ID {insert_reservation_id} nie istnieje w tabeli rezerwacji.")

                # Pobranie i zmodyfikowanie daty rezerwacji
                modified_meeting_date = room_service.get_reservation_datetime(insert_reservation_id)
            else:
                modified_meeting_date = None

            # **Walidacja `insert_internal_meeting_status` (niewrażliwa na wielkość liter)**
            valid_statuses = ["Zaplanowane", "Zakończone", "Odwołane", "Przełożone", "Oczekujące"]
            status_map = {status.lower(): status for status in valid_statuses}

            update_data = {}

            if insert_internal_meeting_status and insert_internal_meeting_status.strip():
                normalized_status = insert_internal_meeting_status.lower()
                insert_internal_meeting_status = status_map.get(normalized_status)

                if insert_internal_meeting_status is None:
                    errors.append(f"Niepoprawny status spotkania. Dozwolone: {', '.join(valid_statuses)}")
                else:
                    update_data["internal_meeting_status"] = insert_internal_meeting_status

            # **Jeśli są błędy, emitujemy je i przerywamy działanie**
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_updateInternalMeeting] Błędy walidacji:\n{error_message}")
                self.internalMeetingUpdateFailed.emit(error_message)
                return

            # **Pobranie obecnych danych spotkania**
            existing_meeting_data = internal_meetings_controller.get_meeting_by_id(insert_meeting_id)
            if not existing_meeting_data:
                self.internalMeetingUpdateFailed.emit(f"Spotkanie o ID {insert_meeting_id} nie istnieje.")
                return

            # **Sprawdzenie, czy istnieją zmiany**
            if insert_meeting_type_id is not None and insert_meeting_type_id != existing_meeting_data["fk_meeting_type_id"]:
                update_data["fk_meeting_type_id"] = insert_meeting_type_id
            if insert_reservation_id is not None and insert_reservation_id != existing_meeting_data["fk_reservation_id"]:
                update_data["fk_reservation_id"] = insert_reservation_id
            if modified_meeting_date is not None and modified_meeting_date != existing_meeting_data["meeting_date"]:
                update_data["meeting_date"] = modified_meeting_date
            if insert_notes is not None and insert_notes.strip() and insert_notes != existing_meeting_data["notes"]:
                update_data["notes"] = insert_notes

            if not update_data:
                self.internalMeetingUpdateFailed.emit("Brak zmian w danych do aktualizacji.")
                return

            # **Aktualizacja spotkania w bazie danych**
            success = internal_meetings_controller.update_meeting(
                meeting_id=insert_meeting_id,
                **update_data  # Przekazujemy tylko pola, które użytkownik zmienił
            )

            if success:
                print(f"[BridgeRoom_updateInternalMeeting] Spotkanie {insert_meeting_id} zostało pomyślnie zaktualizowane!")
                self.internalMeetingUpdatedSuccessfully.emit()
            else:
                self.internalMeetingUpdateFailed.emit("Nie udało się zaktualizować spotkania.")

        except sqlite3.IntegrityError as integrity_error:
            print(f"[BridgeRoom_updateInternalMeeting] Naruszenie integralności bazy danych: {str(integrity_error)}")
            self.internalMeetingUpdateFailed.emit("Błąd: Niepoprawna wartość w bazie danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_updateInternalMeeting] Błąd bazy danych: {str(db_err)}")
            self.internalMeetingAdditionFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_updateInternalMeeting] Błąd klucza w danych: {str(ke)}")
            self.internalMeetingAdditionFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_updateInternalMeeting] Błąd przetwarzania danych: {str(te)}")
            self.internalMeetingAdditionFailed.emit("Błąd przetwarzania danych.")


    # -------------------------------------------------------------------------

    @Slot(int)
    def deleteInternalMeeting(self, insert_meeting_id):
        """
        Usuwa spotkanie wewnętrzne na podstawie podanego meeting_id.

        :param insert_meeting_id: ID spotkania do usunięcia.
        """
        print(f"[BridgeRoom_deleteInternalMeeting] Otrzymano żądanie usunięcia spotkania o ID: {insert_meeting_id}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_deleteInternalMeeting] Brak zalogowanego użytkownika.")
            self.internalMeetingDeletionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            # Inicjalizacja kontrolerów
            room_service = RoomService(self.main_controller)
            internal_meetings_controller = InternalMeetingsController(self.main_controller.db_controller)

            # Pobranie wszystkich `meeting_id` z bazy
            all_meeting_ids = room_service.get_all_meeting_ids()

            # Sprawdzenie, czy podany `insert_meeting_id` istnieje w bazie
            if insert_meeting_id not in all_meeting_ids:
                msg = f"Spotkanie o ID ({insert_meeting_id}) nie istnieje w bazie."
                print(f"[BridgeRoom_deleteInternalMeeting] {msg}")
                self.internalMeetingDeletionFailed.emit(msg)
                return

            # Próba usunięcia spotkania
            success = internal_meetings_controller.delete_meeting(insert_meeting_id)

            if success:
                print(f"[BridgeRoom_deleteInternalMeeting] Spotkanie o ID {insert_meeting_id} zostało pomyślnie usunięte.")
                self.internalMeetingDeletedSuccessfully.emit()
            else:
                print(f"[BridgeRoom_deleteInternalMeeting] Nie udało się usunąć spotkania o ID {insert_meeting_id}.")
                self.internalMeetingDeletionFailed.emit("Nie udało się usunąć spotkania.")

        except ValueError as ve:
            print(f"[BridgeRoom_deleteInternalMeeting] Błąd wartości: {str(ve)}")
            self.internalMeetingDeletionFailed.emit(str(ve))

        except RuntimeError as rue:
            print(f"[BridgeRoom_deleteInternalMeeting] Błąd bazy danych: {str(rue)}")
            self.internalMeetingDeletionFailed.emit("Błąd systemu podczas usuwania spotkania.")

        except KeyError as ke:
            print(f"[BridgeRoom_deleteInternalMeeting] Błąd klucza w danych: {str(ke)}")
            self.internalMeetingDeletionFailed.emit("Błąd w strukturze danych.")


    # -------------------------------------------------------------------------

    @Slot(str, str, str, str)
    def addInternalMeetingParticipant(self, insert_meeting_id, insert_employee_id, insert_participant_role, insert_attendance):
        """
        Dodaje uczestnika do spotkania wewnętrznego po zweryfikowaniu poprawności danych.

        :param insert_meeting_id: ID spotkania.
        :param insert_employee_id: ID pracownika.
        :param insert_participant_role: Rola uczestnika (Organizator, Uczestnik).
        :param insert_attendance: Status obecności (Obecny, Nieobecny, Usprawiedliwiony).
        """
        print(f"[BridgeRoom_addInternalMeetingParticipant] Otrzymano dane: MeetingID={insert_meeting_id}, "
            f"EmployeeID={insert_employee_id}, Role={insert_participant_role}, Attendance={insert_attendance}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_addInternalMeetingParticipant] Brak zalogowanego użytkownika.")
            self.internalMeetingParticipantAdditionFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []  # Lista błędów walidacyjnych

        try:
            # Konwersja ID na int
            try:
                insert_meeting_id = int(insert_meeting_id)
                insert_employee_id = int(insert_employee_id)
            except ValueError:
                self.internalMeetingParticipantAdditionFailed.emit("ID spotkania oraz ID pracownika muszą być liczbami całkowitymi.")
                return

            # Inicjalizacja kontrolerów
            room_service = RoomService(self.main_controller)
            employees_controller = EmployeesController(self.main_controller.db_controller)
            meeting_participants_controller = MeetingParticipantsController(self.main_controller.db_controller)

            # **Sprawdzenie czy `insert_meeting_id` istnieje w systemie**
            all_meeting_ids = room_service.get_all_meeting_ids()
            if insert_meeting_id not in all_meeting_ids:
                errors.append(f"Spotkanie o ID {insert_meeting_id} nie istnieje w systemie.")

            # **Sprawdzenie czy `insert_employee_id` istnieje w systemie**
            all_employee_ids = employees_controller.get_all_employee_ids()
            if insert_employee_id not in all_employee_ids:
                errors.append(f"Pracownik o ID {insert_employee_id} nie istnieje w systemie.")

            # **Walidacja `insert_participant_role` oraz `insert_attendance` (niewrażliwa na wielkość liter)**
            valid_roles = ["Organizator", "Uczestnik"]
            valid_attendances = ["Obecny", "Nieobecny", "Usprawiedliwiony"]

            insert_participant_role = insert_participant_role.capitalize()
            insert_attendance = insert_attendance.capitalize()

            if insert_participant_role not in valid_roles:
                errors.append(f"Niepoprawna rola uczestnika (pracownika): {insert_participant_role}. Dozwolone: {', '.join(valid_roles)}")

            if insert_attendance not in valid_attendances:
                errors.append(f"Niepoprawny status obecności: {insert_attendance}. Dozwolone: {', '.join(valid_attendances)}")

            # **Jeśli są błędy, emitujemy je i przerywamy działanie**
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_addInternalMeetingParticipant] Błędy walidacji:\n{error_message}")
                self.internalMeetingParticipantAdditionFailed.emit(error_message)
                return

            # **Dodanie uczestnika do spotkania**
            success = meeting_participants_controller.add_participant(
                fk_meeting_id=insert_meeting_id,
                fk_employee_id=insert_employee_id,
                participant_role=insert_participant_role,
                attendance=insert_attendance
            )

            if success:
                print(f"[BridgeRoom_addInternalMeetingParticipant] Uczestnik został dodany pomyślnie! MeetingID: {insert_meeting_id}, EmployeeID: {insert_employee_id}")
                self.internalMeetingParticipantAddedSuccessfully.emit()
            else:
                print("[BridgeRoom_addInternalMeetingParticipant] Nie udało się dodać uczestnika do spotkania.")
                self.internalMeetingParticipantAdditionFailed.emit("Wystąpił problem podczas dodawania uczestnika.")

        except sqlite3.OperationalError as op_err:
            print(f"[BridgeRoom_addInternalMeetingParticipant] Błąd operacyjny bazy danych: {str(op_err)}")
            self.internalMeetingParticipantAdditionFailed.emit("Błąd operacyjny bazy danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_addInternalMeetingParticipant] Błąd bazy danych: {str(db_err)}")
            self.internalMeetingParticipantAdditionFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_addInternalMeetingParticipant] Błąd klucza w danych: {str(ke)}")
            self.internalMeetingParticipantAdditionFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_addInternalMeetingParticipant] Błąd przetwarzania danych: {str(te)}")
            self.internalMeetingParticipantAdditionFailed.emit("Błąd przetwarzania danych.")


    # -------------------------------------------------------------------------

    @Slot(str, str, str, str, str)
    def updateInternalMeetingParticipant(
        self, 
        insert_participant_id, 
        insert_meeting_id=None, 
        insert_employee_id=None, 
        insert_participant_role=None, 
        insert_attendance=None
    ):
        """
        Aktualizuje uczestnika spotkania wewnętrznego po zweryfikowaniu poprawności danych.

        :param insert_participant_id: ID uczestnika do aktualizacji (wymagane).
        :param insert_meeting_id: (Opcjonalne) Nowe ID spotkania.
        :param insert_employee_id: (Opcjonalne) Nowe ID pracownika.
        :param insert_participant_role: (Opcjonalne) Nowa rola uczestnika (Organizator, Uczestnik).
        :param insert_attendance: (Opcjonalne) Nowy status obecności (Obecny, Nieobecny, Usprawiedliwiony).
        """
        print(f"[BridgeRoom_updateInternalMeetingParticipant] Otrzymano dane: ParticipantID={insert_participant_id}, "
            f"MeetingID={insert_meeting_id}, EmployeeID={insert_employee_id}, "
            f"Role={insert_participant_role}, Attendance={insert_attendance}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_updateInternalMeetingParticipant] Brak zalogowanego użytkownika.")
            self.internalMeetingParticipantUpdateFailed.emit("Brak zalogowanego użytkownika.")
            return

        errors = []  # Lista błędów walidacyjnych

        try:
            # **Konwersja ID na int tylko jeśli wartości są podane**
            try:
                insert_participant_id = int(insert_participant_id)  # ID uczestnika jest wymagane
                insert_meeting_id = int(insert_meeting_id) if insert_meeting_id and insert_meeting_id.strip() else None
                insert_employee_id = int(insert_employee_id) if insert_employee_id and insert_employee_id.strip() else None
            except ValueError:
                self.internalMeetingParticipantUpdateFailed.emit("ID uczestnika, ID spotkania oraz ID pracownika muszą być liczbami całkowitymi.")
                return

            # **Inicjalizacja kontrolerów**
            room_service = RoomService(self.main_controller)
            employees_controller = EmployeesController(self.main_controller.db_controller)
            meeting_participants_controller = MeetingParticipantsController(self.main_controller.db_controller)

            # **Sprawdzenie czy `insert_participant_id` istnieje**
            all_participant_ids = room_service.get_all_participant_ids()
            if insert_participant_id not in all_participant_ids:
                errors.append(f"Uczestnik o ID {insert_participant_id} nie istnieje w systemie.")

            # **Sprawdzenie czy `insert_meeting_id` istnieje (jeśli podano)**
            if insert_meeting_id is not None:
                all_meeting_ids = room_service.get_all_meeting_ids()
                if insert_meeting_id not in all_meeting_ids:
                    errors.append(f"Spotkanie o ID {insert_meeting_id} nie istnieje w systemie.")

            # **Sprawdzenie czy `insert_employee_id` istnieje (jeśli podano)**
            if insert_employee_id is not None:
                all_employee_ids = employees_controller.get_all_employee_ids()
                if insert_employee_id not in all_employee_ids:
                    errors.append(f"Pracownik o ID {insert_employee_id} nie istnieje w systemie.")

            # **Walidacja `insert_participant_role` oraz `insert_attendance` (niewrażliwa na wielkość liter)**
            valid_roles = ["Organizator", "Uczestnik"]
            valid_attendances = ["Obecny", "Nieobecny", "Usprawiedliwiony"]

            role_map = {role.lower(): role for role in valid_roles}
            attendance_map = {status.lower(): status for status in valid_attendances}

            update_data = {}

            if insert_participant_role and insert_participant_role.strip():
                insert_participant_role = role_map.get(insert_participant_role.lower())
                if insert_participant_role is None:
                    errors.append(f"Niepoprawna rola uczestnika. Dozwolone: {', '.join(valid_roles)}")
                else:
                    update_data["participant_role"] = insert_participant_role

            if insert_attendance and insert_attendance.strip():
                insert_attendance = attendance_map.get(insert_attendance.lower())
                if insert_attendance is None:
                    errors.append(f"Niepoprawny status obecności. Dozwolone: {', '.join(valid_attendances)}")
                else:
                    update_data["attendance"] = insert_attendance

            # **Jeśli są błędy, emitujemy je i przerywamy działanie**
            if errors:
                error_message = "\n".join(errors)
                print(f"[BridgeRoom_updateInternalMeetingParticipant] Błędy walidacji:\n{error_message}")
                self.internalMeetingParticipantUpdateFailed.emit(error_message)
                return

            # **Pobranie obecnych danych uczestnika**
            existing_participant_data = meeting_participants_controller.get_participant_by_id(insert_participant_id)
            if not existing_participant_data:
                self.internalMeetingParticipantUpdateFailed.emit(f"Uczestnik o ID {insert_participant_id} nie istnieje.")
                return

            # **Sprawdzenie, czy istnieją zmiany**
            if insert_meeting_id is not None and insert_meeting_id != existing_participant_data["fk_meeting_id"]:
                update_data["fk_meeting_id"] = insert_meeting_id
            if insert_employee_id is not None and insert_employee_id != existing_participant_data["fk_employee_id"]:
                update_data["fk_employee_id"] = insert_employee_id

            if not update_data:
                self.internalMeetingParticipantUpdateFailed.emit("Brak zmian w danych do aktualizacji.")
                return

            # **Aktualizacja uczestnika w bazie danych**
            success = meeting_participants_controller.update_participant(
                participant_id=insert_participant_id,
                **update_data  # Przekazujemy tylko pola, które mają wartości
            )

            if success:
                print(f"[BridgeRoom_updateInternalMeetingParticipant] Uczestnik {insert_participant_id} został pomyślnie zaktualizowany!")
                self.internalMeetingParticipantUpdatedSuccessfully.emit()
            else:
                self.internalMeetingParticipantUpdateFailed.emit("Nie udało się zaktualizować uczestnika.")

        except sqlite3.IntegrityError as integrity_error:
            print(f"[BridgeRoom_updateInternalMeetingParticipant] Naruszenie integralności bazy danych: {str(integrity_error)}")
            self.internalMeetingParticipantUpdateFailed.emit("Błąd: Niepoprawna wartość w bazie danych.")

        except sqlite3.DatabaseError as db_err:
            print(f"[BridgeRoom_updateInternalMeetingParticipant] Błąd bazy danych: {str(db_err)}")
            self.internalMeetingParticipantAdditionFailed.emit("Błąd bazy danych.")

        except KeyError as ke:
            print(f"[BridgeRoom_updateInternalMeetingParticipant] Błąd klucza w danych: {str(ke)}")
            self.internalMeetingParticipantAdditionFailed.emit("Błąd w strukturze danych.")

        except TypeError as te:
            print(f"[BridgeRoom_updateInternalMeetingParticipant] Błąd przetwarzania danych: {str(te)}")
            self.internalMeetingParticipantAdditionFailed.emit("Błąd przetwarzania danych.")


    # -------------------------------------------------------------------------

    @Slot(int)
    def deleteParticipant(self, insert_participant_id):
        """
        Usuwa uczestnika spotkania na podstawie podanego participant_id.

        :param insert_participant_id: ID uczestnika do usunięcia.
        """
        print(f"[BridgeRoom_deleteParticipant] Otrzymano żądanie usunięcia uczestnika o ID: {insert_participant_id}")

        if self._logged_in_user_id is None:
            print("[BridgeRoom_deleteParticipant] Brak zalogowanego użytkownika.")
            self.participantDeletionFailed.emit("Brak zalogowanego użytkownika.")
            return

        try:
            room_service = RoomService(self.main_controller)
            meeting_participants_controller = MeetingParticipantsController(self.main_controller.db_controller)

            # **Pobranie wszystkich participant_id z bazy**
            all_participant_ids = room_service.get_all_participant_ids()

            # **Sprawdzenie, czy `insert_participant_id` istnieje w bazie**
            if insert_participant_id not in all_participant_ids:
                msg = f"Uczestnik o ID ({insert_participant_id}) nie istnieje w bazie."
                print(f"[BridgeRoom_deleteParticipant] {msg}")
                self.participantDeletionFailed.emit(msg)
                return

            # **Próba usunięcia uczestnika**
            success = meeting_participants_controller.delete_participant(insert_participant_id)

            if success:
                print(f"[BridgeRoom_deleteParticipant] Uczestnik o ID {insert_participant_id} został usunięty.")
                self.participantDeletedSuccessfully.emit()
            else:
                print("[BridgeRoom_deleteParticipant] Nie udało się usunąć uczestnika.")
                self.participantDeletionFailed.emit("Nie udało się usunąć uczestnika.")

        except ValueError as ve:
            print(f"[BridgeRoom_deleteParticipant] Błąd wartości: {str(ve)}")
            self.participantDeletionFailed.emit(str(ve))

        except RuntimeError as rue:
            print(f"[BridgeRoom_deleteParticipant] Błąd bazy danych: {str(rue)}")
            self.participantDeletionFailed.emit("Błąd systemu podczas usuwania uczestnika.")

        except KeyError as ke:
            print(f"[BridgeRoom_deleteParticipant] Błąd klucza w danych: {str(ke)}")
            self.participantDeletionFailed.emit("Błąd w strukturze danych.")


    # ------------------------------------------------------------------------

    @Slot()
    def updateMeetingParticipantsList(self):
        """
        Pobiera listę uczestników spotkań i emituje sygnał do QML.
        """
        try:
            # Pobranie danych uczestników spotkań z serwisu pokoi
            room_service = RoomService(self.main_controller)
            meeting_participants_list = room_service.get_meeting_participants_table()

            # Debugowanie pobranych danych
            # print(f"[BridgeRoom_updateMeetingParticipantsList] Pobranie uczestników spotkań: {meeting_participants_list}")

            # Aktualizacja listy uczestników spotkań
            self._meeting_participants_list = meeting_participants_list

            # Emitowanie sygnału z listą uczestników spotkań
            self.meetingParticipantsListChanged.emit(self._meeting_participants_list)

        except KeyError as ke:
            print(f"[BridgeRoom_updateMeetingParticipantsList] Klucz nie znaleziony w danych uczestników spotkań: {ke}")
            self.meetingParticipantsListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except ValueError as ve:
            print(f"[BridgeRoom_updateMeetingParticipantsList] Błąd w wartościach danych uczestników spotkań: {ve}")
            self.meetingParticipantsListChanged.emit([])  # Emituj pustą listę w przypadku błędu
        except RuntimeError as rue:
            print(f"[BridgeRoom_updateMeetingParticipantsList] Błąd bazy danych: {rue}")
            self.meetingParticipantsListChanged.emit([])  # Emituj pustą listę w przypadku błędu

    @Slot(result=list)
    def getMeetingParticipantsList(self):
        """
        Zwraca listę uczestników spotkań.
        """
        return self._meeting_participants_list


    # -------------------------------------------------------------------------
