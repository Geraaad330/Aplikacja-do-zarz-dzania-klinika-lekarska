# pylint: skip-file

from models.appointments import Appointments
from controllers.database_controller import DatabaseController
import sqlite3


def load_appointments_data_from_file(file_path):
    """
    Wczytuje dane wizyt z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi wizyt.
    :return: Lista krotek z danymi wizyt.
    """
    appointments_records = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:  # Pomijamy puste linie
                continue
            try:
                # Rozdzielanie danych według przecinków
                columns = [col.strip() for col in line.split(',')]
                if len(columns) != 7:
                    raise ValueError(f"Niewłaściwa liczba kolumn w wierszu {line_number}.")
                
                # Odczytujemy dane zgodnie z nową strukturą
                appointment_id = int(columns[0])
                fk_assignment_id = int(columns[1])
                fk_service_id = int(columns[2])
                fk_reservation_id = int(columns[3])
                appointment_date = columns[4]
                appointment_status = columns[5]
                notes = columns[6]

                appointments_records.append((
                    appointment_id,
                    fk_assignment_id,
                    fk_service_id,
                    fk_reservation_id,
                    appointment_date,
                    appointment_status,
                    notes
                ))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return appointments_records



def clear_appointments(controller):
    """
    Usuwa wszystkie wizyty z tabeli `appointments` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        # Usuwanie wszystkich rekordów z tabeli
        controller.connection.execute("DELETE FROM appointments")
        
        # Resetowanie licznika autoincrement
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'appointments'")
        
        controller.connection.commit()
        print("Wszystkie wizyty zostały usunięte z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")


def add_appointments_to_database(data, controller):
    """
    Dodaje listę wizyt do bazy danych za pomocą klasy Appointments.
    Dodano debugowanie do monitorowania procesu.

    :param data: Lista krotek z danymi wizyt.
    :param controller: Obiekt kontrolera bazy danych.
    """
    appointment_model = Appointments(controller)
    try:
        appointment_model.create_table()  # Tworzy tabelę `appointments`, jeśli nie istnieje
        print("Tabela 'appointments' została utworzona lub już istnieje.")
    except Exception as e:
        print(f"Błąd podczas tworzenia tabeli 'appointments': {e}")
        return

    for i, record in enumerate(data, start=1):
        try:
            # Debugowanie: logowanie danych przed wstawieniem
            print(f"[DEBUG] Próbuję dodać rekord {i}: {record}")
            
            # Dodanie wizyty do bazy
            appointment_model.add_appointment(*record[1:])  # Pomijamy appointment_id
            print(f"✔️ Dodano wizytę {i}: Pacjent ID {record[0]}, Pracownik ID {record[1]}, Data {record[4]}.")
        
        except ValueError as e:
            print(f"⚠️ Błąd walidacji przy dodawaniu wizyty {i}: {record}\nSzczegóły: {e}")
        except RuntimeError as e:
            print(f"❌ Błąd bazy danych przy dodawaniu wizyty {i}: {record}\nSzczegóły: {e}")
        except Exception as e:
            print(f"❓ Niezidentyfikowany błąd przy dodawaniu wizyty {i}: {record}\nSzczegóły: {e}")

    print("Wszystkie rekordy zostały przetworzone.")



if __name__ == "__main__":
    # Ścieżka do pliku z danymi wizyt
    appointments_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\appointments_list_v3.txt"

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich wizyt
    clear_appointments(db_controller)

    # Wczytanie danych z pliku
    appointments_list = load_appointments_data_from_file(appointments_file)

    # Dodanie wizyt do bazy danych
    add_appointments_to_database(appointments_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
