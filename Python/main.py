
# pylint: disable=no-name-in-module, import-error
"""importy"""
import os
import sys
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Property, QTimer
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtGui import QGuiApplication, Qt
from PySide6.QtQml import QQmlApplicationEngine
from autogen.settings import url, import_paths
from controllers.main_controller import MainController
from gui.backend_bridge import BackendBridge   # Import klasy Backend
from gui.bridge_employee import BridgeEmployee
from gui.bridge_room import BridgeRoom
from gui.bridge_admin import BridgeAdmin


QQuickStyle.setStyle("Basic")  # Możliwe wartości: "Basic" "Material" "Fusion" "Imagine" "Default"

def resource_path(relative_path: str) -> Path:
    """
    Zwraca ścieżkę do zasobu, działającą zarówno w trybie developerskim, jak i po skompilowaniu do exe.
    """
    if getattr(sys, 'frozen', False):
        # W trybie frozen (exe) zasoby znajdują się w sys._MEIPASS
        base_path = Path(sys._MEIPASS) # pylint: disable=protected-access
    else:
        # W trybie deweloperskim zakładamy, że plik main.py znajduje się w folderze Python,
        # a zasoby są w folderze nadrzędnym
        base_path = Path(__file__).parent.parent
    return base_path / relative_path

# --------------------------------------------------------------------------------------------------

class GeometryManager(QObject):
    """Ustawienia trybu pełnoekranowego/okienkowego"""
    fullScreenChanged = Signal(bool)

    def __init__(self, window):
        super().__init__()
        self.main_window = window
        self._fullscreen = False  # True # False # Domyślny tryb okienkowy

        # Inicjalizacja okna z opóźnionym wymuszeniem trybu okienkowego
        self.initialize_window()

    def initialize_window(self):
        """Inicjalizacja okna w zależności od trybu."""
        if self._fullscreen: # if self._fullscreen = True
            # Domyślnie pełnoekranowy
            self.main_window.setFlags(Qt.Window | Qt.FramelessWindowHint)
            self.main_window.showFullScreen()
        else:
            # Domyślnie okienkowy
            self.main_window.setFlags(
                Qt.Window
                | Qt.CustomizeWindowHint
                | Qt.WindowTitleHint
                | Qt.WindowMinMaxButtonsHint
                | Qt.WindowCloseButtonHint
            )
            self.main_window.setGeometry(100, 100, 1280, 720)  # Pozycja i rozmiar okna
            self.main_window.showNormal()

            # Opóźnione odświeżenie tylko w przypadku trybu okienkowego
            QTimer.singleShot(50, self.force_refresh_window_mode)

    def force_refresh_window_mode(self):
        """Wymusza poprawną inicjalizację stanu okna tylko w trybie okienkowym."""
        if not self._fullscreen:
            self.set_fullscreen(True)
            self.set_fullscreen(False)

    def get_fullscreen(self):
        """pobiera tryb"""
        return self._fullscreen

    def set_fullscreen(self, value):
        """ustawia tryb"""
        if self._fullscreen != value:
            self._fullscreen = value
            self.update_window_mode()
            self.fullScreenChanged.emit(self._fullscreen)

    def update_window_mode(self):
        """aktualizuje tryb"""
        if self._fullscreen:
            # Tryb pełnoekranowy
            self.main_window.setFlags(Qt.Window | Qt.FramelessWindowHint)
            self.main_window.showFullScreen()
        else:
            # Tryb okienkowy z paskiem tytułu
            self.main_window.setFlags(
                Qt.Window
                | Qt.CustomizeWindowHint
                | Qt.WindowTitleHint
                | Qt.WindowMinMaxButtonsHint
                | Qt.WindowCloseButtonHint
            )
            self.main_window.setGeometry(100, 100, 1280, 720)
            self.main_window.showNormal()

    fullscreen = Property(bool, get_fullscreen, set_fullscreen, notify=fullScreenChanged)




 # --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Używamy resource_path, aby ustalić poprawną ścieżkę do importów
    app_dir = resource_path("")
    engine.addImportPath(os.fspath(app_dir))
    for path in import_paths:
        engine.addImportPath(os.fspath(app_dir / path))

    # Integracja z MainController
    main_controller = MainController()
    main_controller.initialize_application()

    # Tworzenie instancji klasy BackendBridge
    backend_bridge = BackendBridge(main_controller)

    print("Rejestracja backendBridge w QML")
    # Rejestracja obiektu Backend w kontekście QML
    engine.rootContext().setContextProperty("backendBridge", backend_bridge)

    bridge_employee = BridgeEmployee(main_controller)  # Drugi backend bridge
    backend_bridge.bridge_employee = bridge_employee  # Dodaj referencję
    print("Rejestracja bridgeEmployee w QML")
    engine.rootContext().setContextProperty("bridgeEmployee", bridge_employee)

    bridge_room = BridgeRoom(main_controller)  # Drugi backend bridge
    backend_bridge.bridge_room = bridge_room  # Dodaj referencję
    print("Rejestracja bridgeRoom w QML")
    engine.rootContext().setContextProperty("bridgeRoom", bridge_room)

    bridge_admin = BridgeAdmin(main_controller)  # Drugi backend bridge
    backend_bridge.bridge_admin = bridge_admin  # Dodaj referencję
    print("Rejestracja bridgeAdmin w QML")
    engine.rootContext().setContextProperty("bridgeAdmin", bridge_admin)

    # Skalowanie DPI
    logical_dpi = app.primaryScreen().logicalDotsPerInch() / 96.0  # Zakładając bazowe DPI 96
    print(f"DPI Scaling Factor: {logical_dpi}")  # Wyświetlenie wartości
    engine.rootContext().setContextProperty("dpiScalingFactor", logical_dpi)

 # ------------------------------------------------------------------------------------------------

    # Ładowanie pliku QML przy użyciu resource_path
    qml_file = os.fspath(resource_path(url))
    print(f"Ładowanie pliku QML: {qml_file}")
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)

    # Pobierz główny obiekt okna
    root_objects = engine.rootObjects()
    main_window = root_objects[0] if len(root_objects) > 0 else None

    # Tworzenie managera geometrii i rejestracja w QML
    geometry_manager = GeometryManager(main_window)
    engine.rootContext().setContextProperty("geometryManager", geometry_manager)

    screens = QGuiApplication.screens()  # Pobierz listę ekranów
    for i, screen in enumerate(screens):
        print(f"Monitor {i}:")
        print(f"  Rozdzielczość: {screen.geometry()}")  # Rozdzielczość
        print(f"  DPI poziome: {screen.logicalDotsPerInchX()}")  # DPI w poziomie
        print(f"  DPI pionowe: {screen.logicalDotsPerInchY()}")  # DPI w pionie
        print(f"  Średnie DPI: {screen.logicalDotsPerInch()}")  # Średnie DPI
        print(f"  Skala: {screen.devicePixelRatio()}")  # Skala (dla ekranów HiDPI)
        print()

    # ZMIANA MONITORA 
    # tylko dla trybu pełnoekranowego
    selected_geometry = screens[0].geometry()  
    main_window.setGeometry(selected_geometry)

    # Sprawdź, na którym monitorze aplikacja jest uruchomiona
    main_window_screen = main_window.screen()
    if main_window_screen:
        print("Aplikacja jest przypisana do monitora:")
        print(f" Nazwa: {main_window_screen.name()}")
        print(f" Geometria: {main_window_screen.geometry()}")  # Rozdzielczość logiczna
        print(f" Skala: {main_window_screen.devicePixelRatio()}")  # Skalowanie DPI
    else:
        print("Nie można zidentyfikować monitora przypisanego do okna aplikacji.")


 # ------------------------------------------------------------------------------------------------

    try:
        # Funkcja sys.exit() kończy działanie programu
        sys.exit(app.exec())

    finally:
        # Gwarantowane zamknięcie aplikacji
        main_controller.shutdown_application()