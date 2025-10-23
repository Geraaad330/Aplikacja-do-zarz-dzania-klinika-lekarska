from models.prescriptions import Prescriptions
from controllers.database_controller import DatabaseController
import sqlite3

def load_prescription_data_from_file(file_path):
    """
    Wczytuje dane recept z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi recept.
    :return: Lista krotek z danymi recept.
    """
    prescription_records = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:  # Pomijamy puste linie
                continue
            try:
                # Rozdzielanie danych według przecinków
                columns = [col.strip() for col in line.split(',')]
                if len(columns) != 6:
                    raise ValueError(f"Niewłaściwa liczba kolumn w wierszu {line_number}.")
                
                # Odczytujemy dane
                fk_appointment_id = int(columns[1])
                medicine_name = columns[2]  # Nazwa leku
                dose = int(columns[3])  # Dawka
                price = float(columns[4])  # Cena
                code = columns[5]  # Kod recepty

                prescription_records.append((fk_appointment_id, medicine_name, dose, price, code))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return prescription_records

def clear_prescriptions(controller):
    """
    Usuwa wszystkie recepty z tabeli `prescriptions` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        # Usuwanie wszystkich rekordów z tabeli
        controller.connection.execute("DELETE FROM prescriptions")
        
        # Resetowanie licznika autoincrement
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'prescriptions'")
        
        controller.connection.commit()
        print("Wszystkie recepty zostały usunięte z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")

def add_prescriptions_to_database(data, controller):
    """
    Dodaje listę recept do bazy danych za pomocą klasy Prescriptions.

    :param data: Lista krotek z danymi recept.
    :param controller: Obiekt kontrolera bazy danych.
    """
    prescription_model = Prescriptions(controller)
    prescription_model.create_table()  # Tworzy tabelę `prescriptions`, jeśli nie istnieje

    for record in data:
        try:
            # Wstawianie danych recepty do bazy
            prescription_model.add_prescription(*record)
            print(f"Dodano receptę: Lek {record[1]} (Dawka: {record[2]} mg, Cena: {record[3]} PLN).")
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Recepta {record[1]} nie została dodana.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Recepta {record[1]} nie została dodana.")

if __name__ == "__main__":
    # Ścieżka do pliku z danymi recept
    prescriptions_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\prescriptions_list.txt"

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich recept
    clear_prescriptions(db_controller)

    # Wczytanie danych z pliku
    prescription_list = load_prescription_data_from_file(prescriptions_file)

    # Dodanie recept do bazy danych
    add_prescriptions_to_database(prescription_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
