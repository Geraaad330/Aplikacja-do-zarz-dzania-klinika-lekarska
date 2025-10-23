from models.patients import Patients
from controllers.database_controller import DatabaseController
import sqlite3


def load_patient_data_from_file(file_path):
    """
    Wczytuje dane pacjentów z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi pacjentów.
    :return: Lista krotek z danymi pacjentów.
    """
    patient_records = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:  # Pomijamy puste linie
                continue
            try:
                # Rozdzielanie danych według przecinków
                columns = [col.strip() for col in line.split(',')]
                if len(columns) != 8:  # Oczekiwane są 8 kolumn bez `is_active`
                    raise ValueError(f"Niewłaściwa liczba kolumn w wierszu {line_number}.")
                
                # Pobranie danych pacjenta
                first_name = columns[1]  # Imię
                last_name = columns[2]  # Nazwisko
                pesel = columns[3]  # PESEL
                phone = columns[4]  # Numer telefonu
                email = columns[5]  # Email
                address = columns[6]  # Adres
                date_of_birth = columns[7]  # Data urodzenia

                patient_records.append((first_name, last_name, pesel, phone, email, address, date_of_birth))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return patient_records



def clear_patients(controller):
    """
    Usuwa wszystkich pacjentów z tabeli `patients` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        # Usuwanie wszystkich rekordów z tabeli
        controller.connection.execute("DELETE FROM patients")
        
        # Resetowanie licznika autoincrement
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'patients'")
        
        controller.connection.commit()
        print("Wszyscy pacjenci zostali usunięci z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")


def add_patients_to_database(data, controller):
    """
    Dodaje listę pacjentów do bazy danych za pomocą klasy Patients.

    :param data: Lista krotek z danymi pacjentów.
    :param controller: Obiekt kontrolera bazy danych.
    """
    patient_model = Patients(controller)
    patient_model.create_table()  # Tworzy tabelę `patients`, jeśli nie istnieje

    for record in data:
        try:
            # Wstawianie danych pacjenta do bazy
            patient_model.add_patient(*record)
            print(f"Dodano pacjenta: {record[0]} {record[1]} ({record[2]}).")
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Pacjent {record[0]} {record[1]} nie został dodany.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Pacjent {record[0]} {record[1]} nie został dodany.")



if __name__ == "__main__":
    # Ścieżka do pliku z danymi pacjentów
    patients_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\patients_list.txt"  # Zmień ścieżkę, jeśli plik znajduje się w innej lokalizacji

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich pacjentów
    clear_patients(db_controller)

    # Wczytanie danych z pliku
    patient_list = load_patient_data_from_file(patients_file)

    # Dodanie pacjentów do bazy danych
    add_patients_to_database(patient_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
