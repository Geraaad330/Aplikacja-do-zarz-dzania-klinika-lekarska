import QtQuick
import QtQuick.Controls

Rectangle {
    id: dashboard
    width: 1920
    height: 1080
    visible: true

    property bool isDarkMode: false


    Timer {
        id: messageTimer
        interval: 10000
        running: false
        repeat: false
        onTriggered: {
            idMessages.text = ""  // Gdy Timer się skończy, czyścimy tekst
        }
    }


    Component.onCompleted: {
        console.log("EmployeeCRUD.qml załadowany, sprawdzanie uprawnień...");
        bridgeEmployee.checkEmployeeCrudAccess("EmployeeCRUD");
    }

    Connections {
        target: bridgeEmployee

        // Obsługa błędu dostępu do EmployeeCRUD
        function onEmployeeErrorOccurred(errorMessage) {
            console.log("[QML] Błąd dostępu: " + errorMessage);

            employeeErrorText.text = errorMessage;
            employeeErrorPopup.open();
        }

        function onEmployeeAdditionFailed(errorMessage) {
            console.log("[QML] Błąd walidacji: " + errorMessage);

            // Ustawienie tekstu błędu
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchamiamy timer, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        function onEmployeeAddedSuccessfully() {
            console.log("DEBUG: onEmployeeAddedSuccessfully fired")
            idMessages.text = qsTr("Pracownik został dodany do bazy danych!")
            messageTimer.start()
        }

        function onEmployeeUpdateFailed(errorMessage) {
            console.log("[QML] Błąd aktualizacji: " + errorMessage);
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;
            messageTimer.restart();
        }

        function onEmployeeUpdatedSuccessfully() {
            console.log("DEBUG: onEmployeeUpdatedSuccessfully fired");
            idMessages.text = qsTr("Pracownik został zaktualizowany pomyślnie!");
            idMessages.visible = true;
            messageTimer.start();
        }

        function onEmployeeDeletedSuccessfully() {
            console.log("[QML] Pracownik usunięty pomyślnie.");
            showValidationMessage("Pracownik został usunięty.");
        }

        function onEmployeeDeletionFailed(errorMessage) {
            console.log("[QML] Błąd usuwania: " + errorMessage);
            showValidationMessage("Błąd: " + errorMessage);
        }

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






    function validateEmptyField(value, fieldName) {
        if (!value || value.trim() === "") {
            showValidationMessage(`${fieldName} nie może być puste.`);
            return false;
        }
        return true; // Gdy wartość nie jest pusta
    }


    function validateNumber(value) {
        let regex = /^\d+$/;
        return regex.test(value);
    }

    // Funkcje walidacyjne
    function validateName(name) {
        let regex = /^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]+$/;
        return regex.test(name);
    }

    function validatePhone(phone) {
        let regex = /^\d{9}$/;
        return regex.test(phone.replace(/\s|-/g, ""));
    }

    function validateEmail(email) {
        let regex = /^[\w\.-]+@[\w\.-]+\.\w+$/;
        return regex.test(email);
    }

    function validateIsMed(isMed) {
        let formattedValue = isMed.trim().toLowerCase();
        return formattedValue === "tak" || formattedValue === "nie";
    }

    function formatIsMed(value) {
        // Usuwa zbędne spacje, konwertuje na małe litery
        return value.trim().toLowerCase();
    }

    function validateIsActive(isActive) {
        let formattedValue = isActive.trim().toLowerCase();
        return formattedValue === "tak" || formattedValue === "nie";
    }

    function formatIsActive(value) {
        // Usuwa zbędne spacje, konwertuje na małe litery
        return value.trim().toLowerCase();
    }

    function validateProfession(profession) {
        let regex = /^[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9,\.\- ]+$/;
        return regex.test(profession);
    }





    function showValidationMessage(message) {
        console.log("Komunikat walidacji:", message);
        idMessages.text = message;
        idMessages.visible = true;

        // Uruchamiamy timer, aby ukryć komunikat po 5 sekundach
        messageTimer.restart();
    }


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
        text: qsTr("Panel pracownicy - zarządzanie pracownikami")
        width: parent.width * 0.55
        height: parent.height * 0.07
        font.pixelSize: Math.min(parent.width * 0.025, parent.height * 0.1)
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

        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
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
        text: qsTr("Dodaj Pracownika")
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
        id: idInputTextContainerFirstNameAdd
        width: parent.width * 0.1
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
            id: addFieldsFirstName
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Imię")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Imię")) {
                    text = ""
                }
            }
        }
    }


    Rectangle {
        id: inputContainerLastLameAdd
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.2
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.16

        TextInput {
            id: addFieldsLastLame
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Nazwisko")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Nazwisko")) {
                    text = ""
                }
            }
        }
    }



    Rectangle {
        id: inputContainerPhoneAdd
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.2
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.27

        TextInput {
            id: addFieldsPhone
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Telefon")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Telefon")) {
                    text = ""
                }
            }
        }


    }

    Rectangle {
        id: inputContainerEmailAdd
        width: parent.width * 0.21
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.26
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.27

        TextInput {
            id: addFieldsEmail
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Email")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Email")) {
                    text = ""
                }
            }
        }


    }

    Rectangle {
        id: inputContainerProfAdd
        width: parent.width * 0.21
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
            id: addFieldsProf
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Zawód")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true   // włączenie przycinania w kontenerze

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Zawód")) {
                    text = ""
                }
            }
        }


    }



    Rectangle {
        id: inputContainerIsMedAdd
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.2
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.38

        TextInput {
            id: addFieldsIsMed
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Personel Med. Tak/Nie")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.009, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Personel Med. Tak/Nie")) {
                    text = ""
                }
            }
        }
    }



    Button {
        id: idButtonPatientsAdd
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: inputContainerIsMedAdd.top
        anchors.topMargin: inputContainerIsMedAdd.height * 0.08
        anchors.left: inputContainerIsMedAdd.right
        anchors.leftMargin: parent.width * 0.02

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
            radius: 15
        }

        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
            text: "Dodaj pracowinka"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");
            let errors = [];

            if (!validateEmptyField(addFieldsFirstName.text, "Imię")) {
                errors.push("Imię nie może być puste.");
            } else if (!validateName(addFieldsFirstName.text)) {
                errors.push("Niepoprawne imię: tylko litery.");
            }

            if (!validateEmptyField(addFieldsLastLame.text, "Nazwisko")) {
                errors.push("Nazwisko nie może być puste.");
            } else if (!validateName(addFieldsLastLame.text)) {
                errors.push("Niepoprawne nazwisko: tylko litery.");
            }

            if (!validateEmptyField(addFieldsPhone.text, "Telefon")) {
                errors.push("Telefon nie może być pusty.");
            } else if (!validatePhone(addFieldsPhone.text)) {
                errors.push("Niepoprawny telefon: 9 cyfr wymagane.");
            }

            if (!validateEmptyField(addFieldsEmail.text, "Email")) {
                errors.push("Email nie może być pusty.");
            } else if (!validateEmail(addFieldsEmail.text)) {
                errors.push("Niepoprawny email.");
            }

            if (!validateEmptyField(addFieldsProf.text, "Zawód")) {
                errors.push("Zawód nie może być pusty.");
            }

            // Walidacja i formatowanie Statusu Medycznego
            let isMedValue = addFieldsIsMed.text.trim(); // Usuwanie spacji

            if (!validateIsMed(isMedValue)) {
                errors.push("Podaj wartość 'Tak' lub 'Nie'.");
            } else {
                isMedValue = formatIsMed(isMedValue); // Konwersja na "Tak" lub "Nie"
            }

            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n"));
            } else {
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");
                bridgeEmployee.addNewEmployee(
                    addFieldsFirstName.text,
                    addFieldsLastLame.text,
                    addFieldsEmail.text,
                    addFieldsPhone.text,
                    addFieldsProf.text,
                    isMedValue // Przesyłamy poprawioną wartość do backendu
                );
            }
        }

    }






    Button {
            id: idButtonPatientsUpdate
            width: parent.width * 0.1
            height: parent.height * 0.042

            anchors.top: inputContainerIsMedUpdaate.top
            anchors.topMargin: inputContainerIsMedUpdaate.height * 0.08
            anchors.leftMargin: parent.width * 0.02
            anchors.left: inputContainerIsMedUpdaate.right

            background: Rectangle {
                color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
                radius: 15
            }

            contentItem: Text {
                color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
                text: "Aktualizuj pracownika"
                font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.35)
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            onClicked: {
                console.log("Przycisk 'Aktualizuj dane' został kliknięty.");
                let errors = [];

                // Walidacja ID pracownika (pole obowiązkowe)
                if (!validateNumber(fieldsIdEmpUpdaate.text)) {
                    errors.push("ID pracownika musi być liczbą.");
                }

                // Opcjonalna walidacja pozostałych pól – walidujemy tylko, gdy pole nie jest puste
                if (fieldsFirstNameUpdaated.text.length > 0 && !validateName(fieldsFirstNameUpdaated.text)) {
                    errors.push("Niepoprawne imię: tylko litery.");
                }
                if (fieldsLastLameUpdaate.text.length > 0 && !validateName(fieldsLastLameUpdaate.text)) {
                    errors.push("Niepoprawne nazwisko: tylko litery.");
                }
                if (fieldsEmailUpdaate.text.length > 0 && !validateEmail(fieldsEmailUpdaate.text)) {
                    errors.push("Niepoprawny email.");
                }
                if (fieldsPhoneUpdaate.text.length > 0 && !validatePhone(fieldsPhoneUpdaate.text)) {
                    errors.push("Niepoprawny telefon: 9 cyfr wymagane.");
                }
                if (fieldsProfUpdaate.text.length > 0 && !validateProfession(fieldsProfUpdaate.text)) {
                    errors.push("Niepoprawny zawód.");
                }

                // Walidacja i formatowanie pola Personel Medyczny – pole opcjonalne
                let isMedValue = fieldsIsMedUpdaate.text.trim();
                if (isMedValue.length > 0 && !validateIsMed(isMedValue)) {
                    errors.push("Podaj wartość 'Tak' lub 'Nie'.");
                } else if (isMedValue.length > 0) {
                    isMedValue = formatIsMed(isMedValue);  // Konwersja na "Tak" lub "Nie"
                }

                let isActiveValue = fieldsIsActiveUpdaate.text.trim();
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
                        bridgeEmployee.updateEmployee(
                            fieldsIdEmpUpdaate.text,
                            fieldsFirstNameUpdaated.text,
                            fieldsLastLameUpdaate.text,
                            fieldsEmailUpdaate.text,
                            fieldsPhoneUpdaate.text,
                            fieldsProfUpdaate.text,
                            isMedValue,
                            isActiveValue
                        );
                    } catch (e) {
                        console.log("Błąd podczas wysyłania do backendu:", e);
                        showValidationMessage("Błąd podczas aktualizacji danych pracownika.");
                    }
                }
            }
    }


    Text {
        id: idTextDelete
        width: parent.width * 0.2 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Usuń dane pracownika")
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
        id: idInputTextContainerDelIdEmp
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
            id: fieldsDelEmpId
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID pracownika")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID pracownika")) {
                    text = ""
                }
            }
        }
    }




    Button {
        id: idButtonPatientsDel
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerDelIdEmp.top
        anchors.topMargin: idInputTextContainerDelIdEmp.height * 0.08
        anchors.leftMargin: parent.width * 0.025 // Margines od prawej krawędzi (2% szerokości)
        anchors.left: idInputTextContainerDelIdEmp.right


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
            text: "usuń pracownika"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }



        onClicked: {
            console.log("Przycisk 'Usuń dane' został kliknięty.");

            let errors = [];

            // Walidacja pola ID pacjenta
            if (!validateEmptyField(fieldsDelEmpId.text, "ID pacjenta")) {
                errors.push("ID pacjenta nie może być puste.");
            } else if (!validateNumber(fieldsDelEmpId.text)) {
                errors.push("ID pacjenta musi być liczbą.");
            }

            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n"));
            } else {
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                try {
                    bridgeEmployee.deleteEmployee(
                        parseInt(fieldsDelEmpId.text),
                    );
                    // showValidationMessage("Dane pacjenta zostały usunięte!");
                } catch (e) {
                    console.log("Błąd podczas wysyłania do backendu:", e);
                    showValidationMessage("Błąd podczas usuwania pacjenta.");
                }
            }
        }
    }



    Text {
        id: idTextUpdate
        width: parent.width * 0.2 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Aktualizuj dane pracownika")
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
        width: parent.width * 0.1
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
            id: fieldsFirstNameUpdaated
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Imię")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Imię")) {
                    text = ""
                }
            }
        }
    }


    Rectangle {
        id: idInputTextContainerIdEmpUpdaate
        width: parent.width * 0.1
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
            id: fieldsIdEmpUpdaate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID pracownika")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID pracownika")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: idInputTextContainerIsActiveUpdaate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.39
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.16

        TextInput {
            id: fieldsIsActiveUpdaate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Aktywny Tak/Nie")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.011, dashboard.height * 0.1)
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
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.45
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.16

        TextInput {
            id: fieldsLastLameUpdaate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Nazwisko")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Nazwisko")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: inputContainerPhoneUpdaate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.45
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.27

        TextInput {
            id: fieldsPhoneUpdaate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Telefon")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Telefon")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: inputContainerEmailUpdaate
        width: parent.width * 0.21
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.51
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.27

        TextInput {
            id: fieldsEmailUpdaate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Email")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Email")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: inputContainerProfsUpdaate
        width: parent.width * 0.21
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
            id: fieldsProfUpdaate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Zawód")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            clip: true   // włączenie przycinania w kontenerze

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Zawód")) {
                    text = ""
                }
            }
        }
    }



    Rectangle {
        id: inputContainerIsMedUpdaate
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.45
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.38

        TextInput {
            id: fieldsIsMedUpdaate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Personel Med. Tak/Nie")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.009, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Personel Med. Tak/Nie")) {
                    text = ""
                }
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
        wrapMode: Text.WordWrap //
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.01, parent.height * 0.1)
    }

}

