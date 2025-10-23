import QtQuick
import QtQuick.Controls

Rectangle {
    id: dashboard
    width: 1920
    height: 1080
    visible: true

    property bool isDarkMode: false


    Image {
        id: background
        //source: "images/background22_1920x1080.png"
        // source: "images/background_dark_4.png"
        source: backendBridge.isDarkMode ? "images/background_dark_4.png" : "images/background22_1920x1080.png"

        //fillMode: Image.PreserveAspectFit
        anchors.fill: parent
        anchors.leftMargin: 0
        anchors.rightMargin: 0
        anchors.topMargin: 0
        anchors.bottomMargin: 0  // Wypełnia cały widok
        fillMode: Image.PreserveAspectCrop
    }

    Timer {
        id: messageTimer
        interval: 10000
        running: false
        repeat: false
        onTriggered: {
            idMessages.text = ""  // Gdy Timer się skończy, czyścimy tekst
        }
    }

    Connections {
        target: bridgeEmployee
        function onEmployeeErrorOccurred(errorMessage) {
            console.log("[QML] Odebrano błąd uprawnień: " + errorMessage);
            employeeErrorText.text = errorMessage;
            employeeErrorPopup.open();
        }

        // Obsługa błędu podczas dodawania usługi
        function onServiceAdditionFailed(errorMessage) {
            console.log("[QML] Błąd dodawania usługi: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        // Obsługa pomyślnego dodania usługi
        function onServiceAddedSuccessfully() {
            console.log("[QML] Usługa została dodana pomyślnie!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Usługa została dodana do bazy danych!");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.start();
        }

        // Obsługa błędu podczas aktualizacji usługi
        function onServiceUpdateFailed(errorMessage) {
            console.log("[QML] Błąd aktualizacji usługi: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        // Obsługa pomyślnej aktualizacji usługi
        function onServiceUpdatedSuccessfully() {
            console.log("[QML] Usługa została zaktualizowana pomyślnie!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Usługa została zaktualizowana!");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.start();
        }

        // Obsługa błędu podczas usuwania usługi
        function onServiceDeletionFailed(errorMessage) {
            console.log("[QML] Błąd usuwania usługi: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        // Obsługa pomyślnego usunięcia usługi
        function onServiceDeletedSuccessfully() {
            console.log("[QML] Usługa została usunięta pomyślnie!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Usługa została usunięta z bazy danych!");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.start();
        }

        // Obsługa błędu podczas dodawania specjalności
        function onSpecialtyAdditionFailed(errorMessage) {
            console.log("[QML] Błąd dodawania specjalności: " + errorMessage);

            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            messageTimer.restart();
        }

        // Obsługa pomyślnego dodania specjalności
        function onSpecialtyAddedSuccessfully() {
            console.log("[QML] Specjalność została dodana pomyślnie!");

            idMessages.text = qsTr("Specjalność została dodana do bazy danych!");
            idMessages.visible = true;

            messageTimer.start();
        }
        // Obsługa błędu podczas aktualizacji specjalności
        function onSpecialtyUpdateFailed(errorMessage) {
            console.log("[QML] Błąd aktualizacji specjalności: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        // Obsługa pomyślnej aktualizacji specjalności
        function onSpecialtyUpdatedSuccessfully() {
            console.log("[QML] Specjalność została zaktualizowana pomyślnie!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Specjalność została zaktualizowana w bazie danych!");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.start();
        }

        // Obsługa błędu podczas usuwania specjalności
        function onSpecialtyDeletionFailed(errorMessage) {
            console.log("[QML] Błąd usuwania specjalności: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        // Obsługa pomyślnego usunięcia specjalności
        function onSpecialtyDeletedSuccessfully() {
            console.log("[QML] Specjalność została usunięta pomyślnie!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Specjalność została usunięta pomyślnie!");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.start();
        }


    }



    Component.onCompleted: {
        console.log("EmployeeServSpecCRUD.qml załadowany, sprawdzanie uprawnień...");
        bridgeEmployee.checkEmployeeCrudAccess("EmployeeServSpecCRUD");
    }

    // Obsługa błędu dostępu do EmployeeCRUD
    function onEmployeeErrorOccurred(errorMessage) {
        console.log("[QML] Błąd dostępu: " + errorMessage);

        employeeErrorText.text = errorMessage;
        employeeErrorPopup.open();
    }

    // Funkcja sprawdzająca, czy pole jest puste
    function validateEmptyField(value) {
        return value.trim().length > 0;
    }

    // Funkcja sprawdzająca, czy wartość jest liczbą całkowitą, nieujemną i niepustą
    function validatePositiveInteger(value) {
        return validateEmptyField(value) && /^\d+$/.test(value) && parseInt(value) > 0;
    }

    // Funkcja sprawdzająca, czy wartość jest liczbą zmiennoprzecinkową, nieujemną i niepustą
    function validatePositiveFloat(value) {
        return validateEmptyField(value) && /^\d+(\.\d+)?$/.test(value) && parseFloat(value) >= 0;
    }

    // Funkcja sprawdzająca, czy wartość spełnia wzorzec dla nazwy usługi
    function validateServiceName(value) {
        let regex = /^[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9,\.\- ]+$/;
        return validateEmptyField(value) && regex.test(value);
    }

    // Funkcja sprawdzająca, czy wartość spełnia wzorzec dla nazwy specjalności
    function validateSpecialityName(value) {
        let regex = /^[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9,\.\- ]+$/;
        return validateEmptyField(value) && regex.test(value);
    }

    // Funkcja sprawdzająca poprawność ID usługi (tylko liczby całkowite nieujemne, większe od 0)
    function validateServiceId(value) {
        return validatePositiveInteger(value);
    }

    // Funkcja sprawdzająca poprawność ID specjalności (tylko liczby całkowite nieujemne, większe od 0)
    function validateSpecialityId(value) {
        return validatePositiveInteger(value);
    }


    function validateIsActive(isActive) {
        let formattedValue = isActive.trim().toLowerCase();
        return formattedValue === "tak" || formattedValue === "nie";
    }

    function formatIsActive(value) {
        // Usuwa zbędne spacje, konwertuje na małe litery
        return value.trim().toLowerCase();
    }


    function showValidationMessage(message) {
        console.log("Komunikat walidacji:", message);
        idMessages.text = message;
        idMessages.visible = true;

        // Uruchamiamy timer, aby ukryć komunikat po 5 sekundach
        messageTimer.restart();
    }


    Popup {
        id: employeeErrorPopup
        modal: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        // Wyśrodkowanie Popup na ekranie
        anchors.centerIn: Overlay.overlay

        // Tło Popup z półprzezroczystością
        background: Rectangle {
            color: "black" // Półprzezroczyste szare tło
            radius: 10         // Zaokrąglone rogi
        }

        // Obsługa zamknięcia Popup
        onClosed: {
            console.log("[QML] Zamknięto komunikat błędu. Przełączanie na EmployeeMainList.qml...");
            mainViewLoader.source = "EmployeeMainList.qml";  // 👈 PRZEŁĄCZ NA EmployeeMainList TYLKO TUTAJ
        }

        Column {
            anchors.centerIn: parent
            spacing: 20

            // Tekst błędu
            Text {
                id: employeeErrorText
                text: "Brak uprawnień do zarządzania pracownikami."
                font.pixelSize: 18
                color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                horizontalAlignment: Text.AlignHCenter
            }

            // Przycisk "OK"
            Button {
                width: parent.width * 0.25
                height: parent.height * 0.4
                text: "OK"

                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: {
                    employeeErrorPopup.close();
                    mainViewLoader.source = "EmployeeMainList.qml"; // 👈 PRZEŁĄCZ TYLKO TUTAJ
                }

                background: Rectangle {
                    color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"
                    radius: 5
                }
            }
        }
    }

    Text {
        id: idBarMenu
        width: idRamka.width * 0.9 // 90% szerokości ramki
        height: idRamka.height * 0.05 // 10% wysokości ramki
        text: qsTr("Menu")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.horizontalCenter: idRamka.horizontalCenter
        anchors.top: idRamka.top
        anchors.topMargin: idRamka.height * 0.03 // Margines między tekstami
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.013, parent.height * 0.1)
    }

    Text {
        id: idBarHarmonogram
        width: idRamka.width * 0.9 // 90% szerokości ramki
        height: idRamka.height * 0.05 // 10% wysokości ramki
        text: qsTr("panel pracownicy")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.horizontalCenter: idRamka.horizontalCenter
        anchors.top: idRamka.top
        anchors.topMargin: idRamka.height * 0.065// Margines między tekstami
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.013, parent.height * 0.1)
    }

    Rectangle {
        id: idRamka
        // Rozmiar ramki proporcjonalny do tła
        width: background.width * 0.13 // 13% szerokości tła
        height: background.height * 0.95 // 95% wysokości tła

        color: "transparent"
        border.color: "white"
        border.width: 5
        radius: 20

        // Wyśrodkowanie ramki względem przycisków i marginesy
        anchors.left: idBackToDashboard.left
        anchors.right: id_quit.right
        anchors.leftMargin: -20
        anchors.rightMargin: -20
        anchors.top: background.top
        anchors.bottom: background.bottom
        anchors.topMargin: background.height * 0.02 // Proporcjonalny margines od góry
        anchors.bottomMargin: background.height * 0.02 // Proporcjonalny margines od dołu
    }


    Rectangle {
        id: customCheckBox
        // width: parent.height * 0.03// Dynamiczny rozmiar checkboxa
        width: Math.min(parent.width * 0.05, parent.height * 0.035) // Skalowanie w poziomie i pionie
        height: width // Zachowanie kwadratowego kształtu
        radius: width * 0.1 // Zaokrąglenia rogów
        // color: checked ? "#22ff00" : "#cccccc" // Kolor w zależności od stanu zaznaczenia
        color: backendBridge.isDarkMode
               ? (checked ? "#118f39" : "#961c3d") // (zaznaczony), (niezaznaczony) dla trybu ciemnego
               : (checked ? "#ffde59" : "#D3D3D3") // (zaznaczony), (niezaznaczony) dla trybu jasnego
        border.color: backendBridge.isDarkMode
                ? (checked ? "#22ff00" : "#ff0000") // (zaznaczony), (niezaznaczony) dla trybu ciemnego
                : (checked ? "#ffde59" : "#D3D3D3") // (zaznaczony), (niezaznaczony) dla trybu jasnego
        border.width: width * 0.05 // Grubość ramki
        anchors.left: idRamka.right
        anchors.leftMargin: idRamka.width * 0.4 // Dynamiczny odstęp od ramki
        anchors.bottom: idRamka.bottom
        anchors.bottomMargin: idRamka.height * 0.03 // Dynamiczny odstęp od dołu (5% wysokości rodzica)


        property bool checked: false // Własna właściwość przechowująca stan
        signal toggled(bool checked) // Sygnał emitowany po zmianie stanu

        MouseArea {
            anchors.fill: parent
            onClicked: {
                customCheckBox.checked = !customCheckBox.checked // Przełącz stan
                customCheckBox.toggled(customCheckBox.checked) // Emituj sygnał
                canvas.requestPaint() // Wymuś odświeżenie płótna
            }
        }

        onCheckedChanged: {
            console.log("Checkbox state changed to: " + checked);
            geometryManager.fullscreen = checked;
        }

        // Symbol "ptaszek" w środku, wyświetlany tylko po zaznaczeniu
        Canvas {
            id: canvas
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d");
                ctx.clearRect(0, 0, width, height); // Wyczyść obszar rysowania
                if (customCheckBox.checked) {
                    ctx.beginPath();
                    ctx.moveTo(width * 0.2, height * 0.5);
                    ctx.lineTo(width * 0.4, height * 0.7);
                    ctx.lineTo(width * 0.8, height * 0.3);
                    ctx.strokeStyle = "#000000"; // Kolor "ptaszka" na czarny
                    ctx.lineWidth = width * 0.1;
                    ctx.stroke();
                }
            }
        }

        // Tekst obok checkboxa
        Text {
            id: textFullSceen
            text: qsTr("Tryb pełnoekranowy")
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.right
            anchors.leftMargin: width * 0.1
            font.pixelSize: parent.height * 0.8 // Dynamiczny rozmiar tekstu (proporcja wysokości rodzica)
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            // clip: true
            // elide: Text.ElideRight
        }

        Component.onCompleted: {
            // Synchronizuj stan checkboxa z aktualnym stanem trybu pełnoekranowego
            customCheckBox.checked = geometryManager.fullscreen;
        }
    }


    Rectangle {
        id: checkBoxDarkMode
        width: Math.min(parent.width * 0.05, parent.height * 0.035) // Skalowanie w poziomie i pionie
        height: width // Zachowanie kwadratowego kształtu
        radius: width * 0.1 // Zaokrąglenia rogów
        color: backendBridge.isDarkMode
               ? (checked ? "#118f39" : "#961c3d") // (zaznaczony), (niezaznaczony) dla trybu ciemnego
               : (checked ? "#ffde59" : "#D3D3D3") // (zaznaczony), (niezaznaczony) dla trybu jasnego
        border.color: backendBridge.isDarkMode
                ? (checked ? "#22ff00" : "#ff0000") // (zaznaczony), (niezaznaczony) dla trybu ciemnego
                : (checked ? "#ffde59" : "#D3D3D3") // (zaznaczony), (niezaznaczony) dla trybu jasnego
        border.width: width * 0.05
        anchors.left: customCheckBox.right
        anchors.leftMargin: customCheckBox.height * 10
        anchors.bottom: customCheckBox.bottom
        anchors.bottomMargin: customCheckBox.height * 0// Dynamiczny odstęp od dołu (5% wysokości rodzica)

        property bool checked: false

        MouseArea {
            anchors.fill: parent
            onClicked: {
                console.log("Kliknięto checkbox trybu ciemnego");
                checkBoxDarkMode.checked = !checkBoxDarkMode.checked;
                backendBridge.isDarkMode = checkBoxDarkMode.checked; // Synchronizacja z backendem
                canvasDark.requestPaint(); // Wymuszenie odświeżenia płótna
            }
        }

        Canvas {
            id: canvasDark
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d");
                ctx.clearRect(0, 0, width, height); // Czyszczenie płótna

                if (checkBoxDarkMode.checked) {
                    ctx.beginPath();
                    ctx.moveTo(width * 0.2, height * 0.5); // Start ptaszka
                    ctx.lineTo(width * 0.4, height * 0.7); // Środek ptaszka
                    ctx.lineTo(width * 0.8, height * 0.3); // Koniec ptaszka
                    ctx.strokeStyle = "#000000"; // Czarny kolor
                    ctx.lineWidth = width * 0.1; // Grubość linii
                    ctx.stroke();
                }
            }
        }

        Text {
            text: qsTr("Tryb ciemny")
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.right
            anchors.leftMargin: width * 0.19
            font.pixelSize: parent.height * 0.8
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            // clip: true
            // elide: Text.ElideRight
        }

        Component.onCompleted: {
            checkBoxDarkMode.checked = backendBridge.isDarkMode;
        }

    }


    // Text {
    //     text: "Fullscreen: " + geometryManager.fullscreen
    //     color: "red"
    //     anchors.bottom: parent.bottom
    //     anchors.bottomMargin: 20
    // }



    Text {
        text: qsTr("Panel pracownicy - zarządzanie usługami i specjalnościami")
        width: parent.width * 0.55
        height: parent.height * 0.07
        font.pixelSize: Math.min(parent.width * 0.021, parent.height * 0.1)
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.04// Proporcjonalne pozycjonowanie
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.15
        anchors.right: background.right
        anchors.rightMargin: background.width * 0.15
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true
        elide: Text.ElideRight
    }

    Button {
        id: idBackToDashboard
        width: parent.width * 0.1
        height: parent.height * 0.042
        font.pixelSize: height * 0.42
        text: "Powrót"
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.12 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Powrót"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // Przełącz widok na Dashboard.qml
            mainViewLoader.source = "Dashboard.qml";
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"
            radius: 15 // Zaokrąglenie rogów o 5 pikseli
        }
    }

    Button {
        id: id_quit
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.05

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Wyjdź z aplikacji"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        // Obsługa kliknięcia
        onClicked: {
            Qt.quit(); // Wyłączenie aplikacji
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }
    }


    Button {
        id: idButtonEmployeeServSpecCRUD
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.51 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Zarządzanie usługami i spec."
            font.pixelSize: Math.min(parent.width * 0.09, parent.height * 0.277)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "EmployeeServSpecCRUD.qml";
            idButtonEmployeeMainList.isClicked = true;
        }

        background: Rectangle {
            color: backendBridge.currentScreen === "EmployeeMainList"
                   ? "#6aa84f" // Kolor dla aktywnego przycisku "#A9A9A9"
                   : backendBridge.isDarkMode ? "#961c3d" : "#ffe599" // Tryb ciemny/jasny
            radius: 15
        }

    }


    Button {
        id: idButtonEmployeeMainList
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.75// Margines od dolnej krawędzi (2% wy

        // Właściwość do przechowywania stanu kliknięcia
        property bool isClicked: false

        // Tło przycisku z dynamiczną zmianą kolorów
        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Lista pracowników"
            font.pixelSize: Math.min(parent.width * 0.095, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // backendBridge.currentScreen = "PatientsMainList"; // Zmiana aktywnej zakładki
            // Przełącz widok na Login.qml
            mainViewLoader.source = "EmployeeMainList.qml";
            // Zmieniamy stan isClicked na true

        }


    }

    Button {
        id: idButtonEmployeeCRUD
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.67 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Zarządzanie pracownikami"
            font.pixelSize: Math.min(parent.width * 0.09, parent.height * 0.3)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }


        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "EmployeeCRUD.qml";
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

    }

    Button {
        id: idButtonEmployeeServSpecList
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.59 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Lista usług i specjalności"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.34)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "EmployeeListServSpec.qml";
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }
    }

    Button {
        id: idButtonEmpServAssignList
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.35 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Przypisania do usług"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.34)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "EmployeeAssignServList.qml";

        }


        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }
    }

    Button {
        id: idButtonEmpSpecAssignList
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.43 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Przypisania do specjalności"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.3)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "EmployeeAssignSpecList.qml";
        }


        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }
    }

    Button {
        id: idButtonEmpServSpecAssignCRUD
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.27 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Zrządzanie przypisaniami"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.34)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "EmployeeAssignServSpecCRUD.qml";

        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }
    }


    Text {
        id: idTextAdd
        width: parent.width * 0.3 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Dodaj usługę")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.15
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }


    Rectangle {
        id: idInputTextContainerDelSpecId
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.65
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.5

        TextInput {
            id: fieldsDelSpecId
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID specjalności")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID specjalności")) {
                    text = ""
                }
            }
        }
    }


    Button {
        id: idButtonSpecDel
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerDelSpecId.top
        anchors.topMargin: idInputTextContainerDelSpecId.height * 0.08
        anchors.leftMargin: parent.width * 0.025 // Margines od prawej krawędzi (2% szerokości)
        anchors.left: idInputTextContainerDelSpecId.right


        // Właściwość do przechowywania stanu kliknięcia
        property bool isClicked: false

        // Tło przycisku z dynamiczną zmianą kolorów
        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "usuń specjalność"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }



        onClicked: {
            console.log("Przycisk 'Usuń dane' został kliknięty.");

            let errors = [];

            // Walidacja pola ID pacjenta
            if (!validateEmptyField(fieldsDelSpecId.text, "ID pacjenta")) {
                errors.push("ID pacjenta nie może być puste.");
            } else if (!validateSpecialityId(fieldsDelSpecId.text)) {
                errors.push("ID pacjenta musi być liczbą.");
            }

            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n"));
            } else {
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                try {
                    bridgeEmployee.deleteSpecialty(
                        parseInt(fieldsDelSpecId.text)
                    );
                    // showValidationMessage("Dane pacjenta zostały usunięte!");
                } catch (e) {
                    console.log("Błąd podczas wysyłania do backendu:", e);
                    showValidationMessage("Błąd podczas usuwania pacjenta.");
                }
            }
        }
    }


    Rectangle {
        id: idInputTextContainerTimeAdd
        width: parent.width * 0.145
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true

        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.2
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: addFieldsTimeAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Czas trwania")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Czas trwania")) {
                    text = ""
                }
            }
        }
    }


    Rectangle {
        id: inputContainerPriceAdd
        width: parent.width * 0.145
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.2
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.205

        TextInput {
            id: addFieldsPriceAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Cena")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Cena")) {
                    text = ""
                }
            }
        }
    }



    Rectangle {
        id: inputContainerAdress
        width: parent.width * 0.3
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true   // włączenie przycinania w kontenerze


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.26
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: addFieldsServNameAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Nazwa usługi")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true   // włączenie przycinania w kontenerze

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Nazwa usługi")) {
                    text = ""
                }
            }
        }


    }





    Button {
        id: idButtonServAdd
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: inputContainerPriceAdd.top
        anchors.topMargin: inputContainerPriceAdd.height * 0.08
        anchors.left: inputContainerPriceAdd.right
        anchors.leftMargin: parent.width * 0.02

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
            radius: 15
        }

        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
            text: "Dodaj usługę"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk 'Dodaj usługę' został kliknięty.");

            let errors = [];

            // Walidacja pól (wszystkie muszą być uzupełnione)
            if (!validateEmptyField(addFieldsTimeAdd.text)) {
                errors.push("Czas trwania nie może być pusty.");
            } else if (!validatePositiveInteger(addFieldsTimeAdd.text)) {
                errors.push("Czas trwania musi być liczbą całkowitą większą od 0.");
            }

            if (!validateEmptyField(addFieldsPriceAdd.text)) {
                errors.push("Cena nie może być pusta.");
            } else if (!validatePositiveFloat(addFieldsPriceAdd.text)) {
                errors.push("Cena musi być liczbą zmiennoprzecinkową większą lub równą 0.");
            }

            if (!validateEmptyField(addFieldsServNameAdd.text)) {
                errors.push("Nazwa usługi nie może być pusta.");
            } else if (!validateServiceName(addFieldsServNameAdd.text)) {
                errors.push("Nazwa usługi zawiera niepoprawne znaki.");
            }

            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n"));
            } else {
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");
                bridgeEmployee.addNewService(
                    addFieldsServNameAdd.text,
                    addFieldsTimeAdd.text,
                    addFieldsPriceAdd.text
                );
            }
        }
    }







    Button {
            id: idButtonSpecUpdate
            width: parent.width * 0.1
            height: parent.height * 0.042

            anchors.top: idInputTextContainerNameSpecUpdate.top
            anchors.topMargin: idInputTextContainerNameSpecUpdate.height * 0.08
            anchors.left: idInputTextContainerNameSpecUpdate.right
            anchors.leftMargin: parent.width * 0.02

            background: Rectangle {
                color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
                radius: 15
            }

            contentItem: Text {
                color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
                text: "Aktualizuj specjalność"
                font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.35)
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            onClicked: {
                console.log("Przycisk 'Aktualizuj dane' został kliknięty.");

                let errors = [];

                // Sprawdzenie pola ID pacjenta (musi być liczbą)
                if (!validateEmptyField(fieldsIdSpecUpdate.text)) {
                    errors.push("Id specjalności nie może być puste.");
                } else if (!validateSpecialityId(fieldsIdSpecUpdate.text)) {
                    errors.push("Id specjalności musi być liczbą całkowitą.");
                }

                // Sprawdzenie pustych pól i ich poprawności
                if (!validateEmptyField(addFieldsNameSpecAdd.text)) {
                    errors.push("ID pacjenta nie może być puste.");
                } else if (!validateSpecialityName(addFieldsNameSpecAdd.text)) {
                    errors.push("ID pacjenta musi być liczbą.");
                }

                let isActiveValue = fieldsIsActiveSpecUpdaate.text.trim();
                if (isActiveValue.length > 0 && !validateIsActive(isActiveValue)) {
                    errors.push("Podaj wartość 'Tak' lub 'Nie' dla pola 'Aktywność'.");
                } else if (isActiveValue.length > 0) {
                    isActiveValue = formatIsActive(isActiveValue);  // Konwersja na "tak" lub "nie"
                }

                if (errors.length > 0) {
                    console.log("Błędy walidacji:", errors);
                    showValidationMessage(errors.join("\n"));
                } else {
                    console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                    try {
                        bridgeEmployee.updateSpecialty(
                            fieldsIdSpecUpdate.text,
                            fieldsNameSpecUpdate.text,
                            isActiveValue
                        );
                        // showValidationMessage("Dane pacjenta zostały zaktualizowane!");
                    } catch (e) {
                        console.log("Błąd podczas wysyłania do backendu:", e);
                        showValidationMessage("Błąd podczas aktualizacji pacjenta.");
                    }
                }
            }
        }


    Text {
        id: idTextDelete
        width: parent.width * 0.2 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Usuń usługę")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.6
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }

    Rectangle {
        id: idInputTextContainerDelId
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.65
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsServIdDel
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID usługi")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID usługi")) {
                    text = ""
                }
            }
        }
    }




    Button {
        id: idButtonServDel
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerDelId.top
        anchors.topMargin: idInputTextContainerDelId.height * 0.08
        anchors.leftMargin: parent.width * 0.025 // Margines od prawej krawędzi (2% szerokości)
        anchors.left: idInputTextContainerDelId.right


        // Właściwość do przechowywania stanu kliknięcia
        property bool isClicked: false

        // Tło przycisku z dynamiczną zmianą kolorów
        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "usuń usługę"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk 'Dodaj usługę' został kliknięty.");

            let errors = [];


            if (!validateEmptyField(fieldsServIdDel.text)) {
                errors.push("ID usługi nie może być puste.");
            } else if (!validateServiceId(fieldsServIdDel.text)) {
                errors.push("ID usługi musi być liczbą całkowitą.");
            }


            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n"));
            } else {
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");
                bridgeEmployee.deleteService(
                    fieldsServIdDel.text
                );
            }
        }

    }



    Text {
        id: idTextUpdate
        width: parent.width * 0.2 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Aktualizuj usługę")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.34
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }

    Rectangle {
        id: idInputTextContainerFirstNameUpdaated
        width: parent.width * 0.145
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.45
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsTimeUpdaate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Czas trwania")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Czas trwania")) {
                    text = ""
                }
            }
        }
    }


    Rectangle {
        id: idInputTextContainerFirstNameUpdaate
        width: parent.width * 0.145
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.39
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsIdServUpdaate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID usługi")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID usługi")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: idInputTextContainerIsActiveServUpdaate
        width: parent.width * 0.145
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.39
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.205

        TextInput {
            id: fieldsIsActiveServUpdaate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Aktywny Tak/Nie")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Aktywny Tak/Nie")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: inputContainerLastLameUpdaate
        width: parent.width * 0.145
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.45
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.205

        TextInput {
            id: fieldsPriceUpdaate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Cena")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Cena")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: inputContainerAdressUpdaate
        width: parent.width * 0.3
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true   // włączenie przycinania w kontenerze


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.51
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsServNameUpdaate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Nazwa usługi")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true   // włączenie przycinania w kontenerze

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Nazwa usługi")) {
                    text = ""
                }
            }
        }
    }

    Button {
        id: idButtonServUpdate
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: inputContainerLastLameUpdaate.top
        anchors.topMargin: inputContainerLastLameUpdaate.height * 0.08
        anchors.left: inputContainerLastLameUpdaate.right
        anchors.leftMargin: parent.width * 0.02

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
            radius: 15
        }

        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
            text: "Aktualizuj usługę"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk 'Aktualizuj usługę' został kliknięty.");

            let errors = [];

            // Sprawdzenie pola ID usługi (musi być liczbą)
            if (!validateEmptyField(fieldsIdServUpdaate.text)) {
                errors.push("ID usługi nie może być puste.");
            } else if (!validateServiceId(fieldsIdServUpdaate.text)) {
                errors.push("ID usługi musi być liczbą całkowitą.");
            }

            // Pozostałe pola mogą być puste, ale jeśli są wypełnione, muszą być poprawne
            if (fieldsTimeUpdaate.text.length > 0 && !validatePositiveInteger(fieldsTimeUpdaate.text)) {
                errors.push("Czas trwania musi być liczbą całkowitą większą od 0.");
            }

            if (fieldsPriceUpdaate.text.length > 0 && !validatePositiveFloat(fieldsPriceUpdaate.text)) {
                errors.push("Cena musi być liczbą zmiennoprzecinkową większą lub równą 0.");
            }

            if (fieldsServNameUpdaate.text.length > 0 && !validateServiceName(fieldsServNameUpdaate.text)) {
                errors.push("Nazwa usługi zawiera niepoprawne znaki.");
            }

            let isActiveValue = fieldsIsActiveServUpdaate.text.trim();
            if (isActiveValue.length > 0 && !validateIsActive(isActiveValue)) {
                errors.push("Podaj wartość 'Tak' lub 'Nie' dla pola 'Aktywność'.");
            } else if (isActiveValue.length > 0) {
                isActiveValue = formatIsActive(isActiveValue);  // Konwersja na "tak" lub "nie"
            }

            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n"));
            } else {
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");
                bridgeEmployee.updateService(
                    fieldsIdServUpdaate.text,
                    fieldsServNameUpdaate.text.length > 0 ? fieldsServNameUpdaate.text : "",
                    fieldsTimeUpdaate.text.length > 0 ? fieldsTimeUpdaate.text : "",
                    fieldsPriceUpdaate.text.length > 0 ? fieldsPriceUpdaate.text : "",
                    isActiveValue
                );
            }
        }
    }





    Text {
        id: idMessages
        width: parent.width * 0.65 // 90% szerokości ramki
        height: parent.height * 0.17 // 10% wysokości ramki
        text: qsTr("")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.72
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05
        // horizontalAlignment: Text.AlignHCenter
        // verticalAlignment: Text.AlignVCenter
        verticalAlignment: TextEdit.AlignBottom   // kluczowa linia
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.01, parent.height * 0.1)
    }

    Text {
        id: idTextAdd1
        width: parent.width * 0.3 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Dodaj specialność")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.15
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.5
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }

    Rectangle {
        id: idInputTextContainerNameSpecAdd
        width: parent.width * 0.23
        height: parent.height * 0.11
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true

        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.2
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.5

        TextInput {
            id: addFieldsNameSpecAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Nazwa specjalności")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            wrapMode: TextInput.Wrap  // Włączenie zawijania tekstu
            inputMethodHints: Qt.ImhMultiLine  // Umożliwienie wpisywania wielu linii
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Nazwa specjalności", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Nazwa specjalności")) {
                    text = ""
                }
            }
        }
    }

    Text {
        id: idTextUpdateSpec
        width: parent.width * 0.2 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Aktualizuj specjalność")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.34
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.5
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }


    Rectangle {
        id: idInputTextContainerIdSpecUpdate
        width: parent.width * 0.11
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.39
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.5

        TextInput {
            id: fieldsIdSpecUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID specjalności")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID specjalności")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: idInputTextContainerIsActiveUpdaateSpec
        width: parent.width * 0.11
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.39
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.62

        TextInput {
            id: fieldsIsActiveSpecUpdaate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Aktywny Tak/Nie")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.012, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Aktywny Tak/Nie")) {
                    text = ""
                }
            }
        }
    }



    Rectangle {
        id: idInputTextContainerNameSpecUpdate
        width: parent.width * 0.23
        height: parent.height * 0.11
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.45
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.5

        TextInput {
            id: fieldsNameSpecUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Nazwa specjalności")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            wrapMode: TextInput.Wrap  // Włączenie zawijania tekstu
            inputMethodHints: Qt.ImhMultiLine  // Umożliwienie wpisywania wielu linii
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Nazwa specjalności")) {
                    text = ""
                }
            }
        }
    }

    Button {
        id: idButtonSpecAdd
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerNameSpecAdd.top
        anchors.topMargin: idInputTextContainerNameSpecAdd.height * 0.08
        anchors.left: idInputTextContainerNameSpecAdd.right
        anchors.leftMargin: parent.width * 0.02

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
            radius: 15
        }

        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
            text: "Dodaj specjalność"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");

            let errors = [];

            // Sprawdzenie pustych pól i ich poprawności
            if (!validateEmptyField(addFieldsNameSpecAdd.text)) {
                errors.push("Id specjalności nie może być puste.");
            } else if (!validateSpecialityName(addFieldsNameSpecAdd.text)) {
                errors.push("Id specjalności musi być liczbą.");
            }


            // Jeśli są błędy walidacji
            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n")); // Wyświetl komunikaty błędów
            } else {
                // Wszystkie dane są poprawne - wysyłamy do backendu
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                bridgeEmployee.addNewSpecialty(
                    addFieldsNameSpecAdd.text
                );
            }
        }
    }

    Text {
        id: idTextDeleteSpec
        width: parent.width * 0.2 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Usuń specjalność")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.6
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.5
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }



}

