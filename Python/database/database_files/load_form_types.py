from models.form_types import FormTypes
from controllers.database_controller import DatabaseController
import sqlite3


def load_form_types_from_file(file_path):
    """
    Wczytuje dane typów formularzy z pliku tekstowego.

    :param file_path: Ścieżka do pliku tekstowego z danymi typów formularzy.
    :return: Lista krotek z danymi typów formularzy.
    """
    form_type_records = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:  # Pomijamy puste linie
                continue
            try:
                # Rozdzielanie danych według przecinków
                columns = [col.strip() for col in line.split(',')]
                if len(columns) != 2:
                    raise ValueError(f"Niewłaściwa liczba kolumn w wierszu {line_number}.")

                form_type_id = int(columns[0])  # ID formularza
                form_type_name = columns[1]  # Nazwa formularza

                form_type_records.append((form_type_id, form_type_name))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - {e}")
    return form_type_records


def clear_form_types(controller):
    """
    Usuwa wszystkie typy formularzy z tabeli `form_types` i resetuje licznik ID.

    :param controller: Obiekt kontrolera bazy danych.
    """
    try:
        controller.connection.execute("DELETE FROM form_types")
        controller.connection.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'form_types'")
        controller.connection.commit()
        print("Wszystkie typy formularzy zostały usunięte z tabeli, licznik ID zresetowany.")
    except sqlite3.OperationalError as e:
        print(f"Błąd operacyjny bazy danych: {e}")
    except sqlite3.DatabaseError as e:
        print(f"Błąd bazy danych: {e}")


def add_form_types_to_database(data, controller):
    """
    Dodaje listę typów formularzy do bazy danych za pomocą klasy FormTypes.

    :param data: Lista krotek z danymi typów formularzy.
    :param controller: Obiekt kontrolera bazy danych.
    """
    form_types_model = FormTypes(controller)
    form_types_model.create_table()  # Tworzy tabelę `form_types`, jeśli nie istnieje

    for record in data:
        try:
            form_types_model.create_new_record(record[1])  # Przekazujemy tylko nazwę formularza
            print(f"Dodano typ formularza: {record[1]}.")
        except ValueError as e:
            print(f"Błąd walidacji: {e} - Formularz {record[1]} nie został dodany.")
        except RuntimeError as e:
            print(f"Błąd bazy danych: {e} - Formularz {record[1]} nie został dodany.")


if __name__ == "__main__":
    # Ścieżka do pliku z danymi typów formularzy
    form_types_file = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\form_types_list.txt"  # Zmień ścieżkę na odpowiednią

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()
    db_controller.connect_to_database()

    # Usuwanie wszystkich typów formularzy
    clear_form_types(db_controller)

    # Wczytanie danych z pliku
    form_types_list = load_form_types_from_file(form_types_file)

    # Dodanie typów formularzy do bazy danych
    add_form_types_to_database(form_types_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
