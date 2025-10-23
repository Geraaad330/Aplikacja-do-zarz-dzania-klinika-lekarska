from models.patient_forms import PatientForms
from controllers.database_controller import DatabaseController
import sqlite3

def load_patient_forms_data_from_file(file_path):
    """
    Wczytuje dane formularzy pacjentów z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi formularzy.
    :return: Lista krotek z danymi formularzy.
    """
    form_records = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:  # Pomijamy puste linie
                continue
            try:
                # Rozdzielanie danych według przecinków
                columns = [col.strip() for col in line.split(',')]
                if len(columns) != 5:
                    raise ValueError(f"Niewłaściwa liczba kolumn w wierszu {line_number}.")

                # Przypisywanie wartości z pliku
                fk_patient_id = int(columns[1])
                fk_form_type_id = int(columns[2])
                submission_date = columns[3]
                content = columns[4]

                form_records.append((fk_patient_id, fk_form_type_id, submission_date, content))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return form_records

def clear_patient_forms(controller):
    """
    Usuwa wszystkie formularze pacjentów z tabeli `patient_forms` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        # Usuwanie wszystkich rekordów z tabeli
        controller.connection.execute("DELETE FROM patient_forms")
        
        # Resetowanie licznika autoincrement
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'patient_forms'")
        
        controller.connection.commit()
        print("Wszystkie formularze pacjentów zostały usunięte z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")

def add_patient_forms_to_database(data, controller):
    """
    Dodaje listę formularzy pacjentów do bazy danych za pomocą klasy PatientForms.

    :param data: Lista krotek z danymi formularzy.
    :param controller: Obiekt kontrolera bazy danych.
    """
    forms_model = PatientForms(controller)
    forms_model.create_table()  # Tworzy tabelę `patient_forms`, jeśli nie istnieje

    for record in data:
        try:
            # Wstawianie danych formularza do bazy
            forms_model.add_form(*record)
            print(f"Dodano formularz pacjenta ID {record[0]} z typem formularza ID {record[1]}.")
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Formularz pacjenta ID {record[0]} nie został dodany.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Formularz pacjenta ID {record[0]} nie został dodany.")

if __name__ == "__main__":
    # Ścieżka do pliku z danymi formularzy pacjentów
    forms_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\patient_forms_list.txt"

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich formularzy pacjentów
    clear_patient_forms(db_controller)

    # Wczytanie danych z pliku
    form_list = load_patient_forms_data_from_file(forms_file)

    # Dodanie formularzy pacjentów do bazy danych
    add_patient_forms_to_database(form_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
