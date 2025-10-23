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
        console.log("Setting current screen to RoomsMainList");
        backendBridge.currentScreen = "RoomsMainList";
        console.log("RoomsCRUD.qml załadowany, sprawdzanie uprawnień...");
        bridgeRoom.checkRoomCrudAccess("RoomsCRUD.qml");
    }

    Connections {
        target: bridgeRoom
        function onRoomErrorOccurred(errorMessage) {
            console.log("[QML] Odebrano błąd uprawnień: " + errorMessage);
            roomErrorText.text = errorMessage;
            roomErrorPopup.open();
        }
        // Obsługa błędu dodawania pokoju
        function onRoomAdditionFailed(errorMessage) {
            console.log("[QML] Błąd dodawania pokoju: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        // Obsługa sukcesu dodania pokoju
        function onRoomAddedSuccessfully() {
            console.log("[QML] Pokój został dodany pomyślnie!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Pokój został dodany do bazy danych!");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        // Obsługa błędu podczas aktualizacji pokoju
        function onRoomUpdateFailed(errorMessage) {
            console.log("[QML] Błąd aktualizacji pokoju: " + errorMessage);
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;
            messageTimer.restart(); // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
        }

        // Obsługa pomyślnej aktualizacji pokoju
        function onRoomUpdatedSuccessfully() {
            console.log("[QML] Pokój został zaktualizowany pomyślnie!");
            idMessages.text = qsTr("Pokój został pomyślnie zaktualizowany!");
            idMessages.visible = true;
            messageTimer.start(); // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
        }

        // Obsługa pomyślnego usunięcia pokoju
        function onRoomDeletedSuccessfully() {
            console.log("[QML] Pokój został pomyślnie usunięty!");
            idMessages.text = qsTr("Pokój został pomyślnie usunięty!");
            idMessages.visible = true;
            messageTimer.start();
        }

        // Obsługa błędu podczas usuwania pokoju
        function onRoomDeletionFailed(errorMessage) {
            console.log("[QML] Błąd usuwania pokoju: " + errorMessage);
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;
            messageTimer.restart();
        }
        // Obsługa błędu podczas dodawania typu pokoju
        function onRoomTypeAdditionFailed(errorMessage) {
            console.log("[QML] Błąd dodawania typu pokoju: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        // Obsługa pomyślnego dodania typu pokoju
        function onRoomTypeAddedSuccessfully() {
            console.log("[QML] Typ pokoju został dodany pomyślnie!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Typ pokoju został dodany do bazy danych!");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.start();
        }


        function onRoomTypeUpdateFailed(errorMessage) {
            console.log("[QML] Błąd aktualizacji typu pokoju: " + errorMessage);

            // Wyświetlenie komunikatu o błędzie
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.restart();
        }

        function onRoomTypeUpdatedSuccessfully() {
            console.log("[QML] Typ pokoju został zaktualizowany pomyślnie!");

            // Wyświetlenie komunikatu o sukcesie
            idMessages.text = qsTr("Typ pokoju został pomyślnie zaktualizowany!");
            idMessages.visible = true;

            // Uruchomienie timera, aby ukryć komunikat po 5 sekundach
            messageTimer.start();
        }

        function onRoomTypeDeletionFailed(errorMessage) {
            console.log("[QML] Błąd usuwania typu pokoju: " + errorMessage);
            idMessages.text = "Błąd: " + errorMessage;
            idMessages.visible = true;
            messageTimer.restart();
        }

        // 🔹 Obsługa pomyślnego usunięcia typu pokoju
        function onRoomTypeDeletedSuccessfully() {
            console.log("[QML] Typ pokoju został pomyślnie usunięty!");
            idMessages.text = qsTr("Typ pokoju został usunięty!");
            idMessages.visible = true;
            messageTimer.start();
        }

    }



    
    // Funkcje walidacyjne
    function validateName(name) {
        let regex = /^[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż ]+$/;
        return regex.test(name);
    }
    
    function showValidationMessage(message) {
        console.log("Komunikat walidacji:", message);
        idMessages.text = message;
        idMessages.visible = true;

        // Uruchamiamy timer, aby ukryć komunikat po 5 sekundach
        messageTimer.restart();
    }
    
    function validateEmptyField(value, fieldName) {
        if (!value || value.trim() === "") {
            showValidationMessage(`${fieldName} nie może być puste.`);
            return false;
        }
        return true; // Gdy wartość nie jest pusta
    }
    // Funkcja sprawdzająca, czy wartość jest liczbą całkowitą, nieujemną i niepustą
    function validatePositiveInteger(value) {
        return validateEmptyField(value) && /^\d+$/.test(value) && parseInt(value) > 0;
    }

    function validateNumber(value) {
        let regex = /^\d+$/;
        return regex.test(value);
    }
    
    Popup {
        id: roomErrorPopup
        modal: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        anchors.centerIn: Overlay.overlay

        background: Rectangle {
            color: "black"
            radius: 10
        }

        onClosed: {
            console.log("[QML] Zamknięto komunikat błędu. Przełączanie na RoomsMainList.qml...");
            mainViewLoader.source = "RoomsMainList.qml";
        }

        Column {
            anchors.centerIn: parent
            spacing: 20

            Text {
                id: roomErrorText
                text: "Brak uprawnień do zarządzania pokojami."
                font.pixelSize: 18
                color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                horizontalAlignment: Text.AlignHCenter
            }

            Button {
                width: parent.width * 0.25
                height: parent.height * 0.4
                text: "OK"

                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: {
                    roomErrorPopup.close();
                    mainViewLoader.source = "RoomsMainList.qml";
                }

                background: Rectangle {
                    color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"
                    radius: 5
                }
            }
        }
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
        font.pixelSize: Math.min(parent.width * 0.012, parent.height * 0.1)
    }

    Text {
        id: idBarHarmonogram
        width: idRamka.width * 0.9 // 90% szerokości ramki
        height: idRamka.height * 0.05 // 10% wysokości ramki
        text: qsTr("pokoje i rezerwacje")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.horizontalCenter: idRamka.horizontalCenter
        anchors.top: idRamka.top
        anchors.topMargin: idRamka.height * 0.065// Margines między tekstami
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.012, parent.height * 0.1)
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
        text: qsTr("Panel pokoje i rezerwacje - zarządzanie pokojami")
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
        id: idButtonRoomsReservation
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.5 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Rezerwacje"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "RoomsReservations.qml";
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

    }

    Button {
        id: idButtonRoomsReservationCRUD
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.4 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Zarządzanie rezerwacjami"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.3)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "RoomsReservationsCRUD.qml";
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

    }


    Button {
        id: idButtonMainRooms
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.7// Margines od dolnej krawędzi (2% wy


        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Pokoje"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // backendBridge.currentScreen = "PatientsMainList"; // Zmiana aktywnej zakładki
            // Przełącz widok na Login.qml
            mainViewLoader.source = "RoomsMainList.qml";
        }


    }

    Button {
        id: idButtonRoomsCRUD
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.6 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Zarządzanie pokojami"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.34)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }


        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "RoomsCRUD.qml";
            // Zmieniamy stan isClicked na true
            idButtonRoomsCRUD.isClicked = true;
        }

        // Właściwość do przechowywania stanu kliknięcia
        property bool isClicked: false

        // Tło przycisku z dynamiczną zmianą kolorów
        background: Rectangle {
            color: backendBridge.currentScreen === "RoomsMainList"
                   ? "#6aa84f" // Kolor dla aktywnego przycisku "#A9A9A9"
                   : backendBridge.isDarkMode ? "#961c3d" : "#ffe599" // Tryb ciemny/jasny
            radius: 15
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
        text: qsTr("Dodaj typ pokoju")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.15
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.5
        // horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        wrapMode: Text.WordWrap //
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }

    Rectangle {
        id: idInputTextContainerNameTypeRoomAdd
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
            id: fieldsNameTypeRoomAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Nazwa typu pokoju")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            wrapMode: TextInput.Wrap  // Włączenie zawijania tekstu
            inputMethodHints: Qt.ImhMultiLine  // Umożliwienie wpisywania wielu linii
            clip: true

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Nazwa specjalności", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Nazwa typu pokoju")) {
                    text = ""
                }
            }
        }
    }

    Text {
        id: idTextUpdateSpec
        width: parent.width * 0.2 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Aktualizuj typ pokoju")
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
        id: idInputTextContainerIdTypeRoomUpdate
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
            id: fieldsIdTypeRoomUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID typu pokoju")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID typu pokoju")) {
                    text = ""
                }
            }
        }
    }





    Rectangle {
        id: idInputTextContainerNameSpecTypeRoomUpdate
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
            id: fieldsNameTypeRoomUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Nazwa typu pokoju")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.014, dashboard.height * 0.1)
            wrapMode: TextInput.Wrap  // Włączenie zawijania tekstu
            inputMethodHints: Qt.ImhMultiLine  // Umożliwienie wpisywania wielu linii
            clip: true
            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Nazwa typu pokoju")) {
                    text = ""
                }
            }
        }
    }

    Button {
        id: idButtonTypeRoomUpdate
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerIdTypeRoomUpdate.top
        anchors.topMargin: idInputTextContainerNameSpecTypeRoomUpdate.height * 0.08
        anchors.left: idInputTextContainerNameSpecTypeRoomUpdate.right
        anchors.leftMargin: parent.width * 0.02

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
            radius: 15
        }

        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
            text: "Aktualizuj typ pokoju"
            font.pixelSize: Math.min(parent.width * 0.09, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");

            let errors = [];

            // Sprawdzenie pustych pól i ich poprawności
            if (!validateEmptyField(fieldsIdTypeRoomUpdate.text)) {
                errors.push("Id typu pokoju nie może być puste.");
            } else if (!validatePositiveInteger(fieldsIdTypeRoomUpdate.text)) {
                errors.push("Id typu pokoju musi być liczbą.");
            }
            
            if (!validateEmptyField(fieldsNameTypeRoomUpdate.text)) {
                errors.push("Nazwa typu pokoju nie może być puste.");
            } else if (!validateName(fieldsNameTypeRoomUpdate.text)) {
                errors.push("Nazwa typu pokoju zawiera niepoprawne znaki.");
            }


            // Jeśli są błędy walidacji
            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n")); // Wyświetl komunikaty błędów
            } else {
                // Wszystkie dane są poprawne - wysyłamy do backendu
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                bridgeRoom.updateRoomType(
                    fieldsIdTypeRoomUpdate.text,
                    fieldsNameTypeRoomUpdate.text
                );
            }
        }
    }


    Button {
        id: idButtonTypeRoomAdd
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerNameTypeRoomAdd.top
        anchors.topMargin: idInputTextContainerNameTypeRoomAdd.height * 0.08
        anchors.left: idInputTextContainerNameTypeRoomAdd.right
        anchors.leftMargin: parent.width * 0.02

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
            radius: 15
        }

        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
            text: "Dodaj typ pokoju"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");

            let errors = [];

            // Sprawdzenie pustych pól i ich poprawności
            if (!validateEmptyField(fieldsNameTypeRoomAdd.text)) {
                errors.push("Nazwa typu pokoju nie może być puste.");
            } else if (!validateName(fieldsNameTypeRoomAdd.text)) {
                errors.push("Nazwa typu pokoju zawiera niepoprawne znaki.");
            }


            // Jeśli są błędy walidacji
            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n")); // Wyświetl komunikaty błędów
            } else {
                // Wszystkie dane są poprawne - wysyłamy do backendu
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                bridgeRoom.addRoomType(
                    fieldsNameTypeRoomAdd.text
                );
            }
        }
    }

    Rectangle {
        id: idInputTextContainerIdTypeRoomDel
        width: parent.width * 0.11
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
            id: fieldsIdTypeRoomDel
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID typu pokoju")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID typu pokoju")) {
                    text = ""
                }
            }
        }
    }

    Text {
        id: idTextDeleteSpec
        width: parent.width * 0.2 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Usuń typ pokoju")
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

    Button {
        id: idButtonTypeRoomDel
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerIdTypeRoomDel.top
        anchors.topMargin: idInputTextContainerIdTypeRoomDel.height * 0.08
        anchors.left: idInputTextContainerIdTypeRoomDel.right
        anchors.leftMargin: parent.width * 0.02

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
            radius: 15
        }

        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
            text: "Usuń typ pokoju"
            font.pixelSize: Math.min(parent.width * 0.09, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");

            let errors = [];

            // Sprawdzenie pustych pól i ich poprawności
            if (!validateEmptyField(fieldsIdTypeRoomDel.text)) {
                errors.push("Id typu pokoju nie może być puste.");
            } else if (!validatePositiveInteger(fieldsIdTypeRoomDel.text)) {
                errors.push("Id typu pokoju musi być liczbą.");
            }


            // Jeśli są błędy walidacji
            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n")); // Wyświetl komunikaty błędów
            } else {
                // Wszystkie dane są poprawne - wysyłamy do backendu
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                bridgeRoom.deleteRoomType(
                    fieldsIdTypeRoomDel.text
                );
            }
        }
    }

    Text {
        id: idRoomTextAdd
        width: parent.width * 0.3 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Dodaj Pokój")
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
        id: inputContainerRoomTypeIdAdd
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.26
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.16

        TextInput {
            id: fieldsRoomTypeIdAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID typu pokoju")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID typu pokoju")) {
                    text = ""
                }
            }
        }
    }

    Button {
        id: idButtonServTabAdd
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerRoomNumberAdd.top
        anchors.topMargin: idInputTextContainerRoomNumberAdd.height * 0.08
        anchors.left: inputContainerRoomTypeIdAdd.right
        anchors.leftMargin: parent.width * 0.025

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
            radius: 15
        }

        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
            text: "Dodaj przypisanie"
            font.pixelSize: Math.min(parent.width * 0.09, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");

            let errors = [];

            // Sprawdzenie pustych pól i ich poprawności
            if (!validateEmptyField(fieldsServTabIdEmpAdd.text)) {
                errors.push("Id pracownika nie może być puste.");
            } else if (!validatePositiveInteger(fieldsServTabIdEmpAdd.text)) {
                errors.push("Id pracownika musi być liczbą.");
            }

            if (!validateEmptyField(addFieldsServTabIdServAdd.text)) {
                errors.push("Id usługi nie może być puste.");
            } else if (!validatePositiveInteger(addFieldsServTabIdServAdd.text)) {
                errors.push("Id usługi musi być liczbą.");
            }

            // Jeśli są błędy walidacji
            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n")); // Wyświetl komunikaty błędów
            } else {
                // Wszystkie dane są poprawne - wysyłamy do backendu
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                bridgeEmployee.addEmployeeToService(
                    fieldsServTabIdEmpAdd.text,
                    addFieldsServTabIdServAdd.text
                );
            }
        }
    }

    Rectangle {
        id: idInputTextContainerRoomNumberAdd
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
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsRoomNumberAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Numer pokoju")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Numer pokoju")) {
                    text = ""
                }
            }
        }
    }




    Rectangle {
        id: inputContainerRoomFloorAdd
        width: parent.width * 0.1
        height: parent.height * 0.05
        border.color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
        border.width: 0.5
        radius: 5
        color: "transparent"
        clip: true // Maskowanie tekstu


        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.26
        anchors.left: idRamka.right
        anchors.leftMargin: background.width * 0.05

        TextInput {
            id: fieldsRoomFloorAdd
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Numer Piętra")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Numer Piętra")) {
                    text = ""
                }
            }
        }
    }



    Text {
        id: idRoomTextUpdate
        width: parent.width * 0.3 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Aktualizuj Pokój")
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
        id: idInputTextContainerRoomIdUpdate
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
            id: fieldsRoomIdUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID pokoju")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID pokoju")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: inputContainerRoomFloorUpdate
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
            id: fieldsRoomFloorUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Numer Piętra")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Numer Piętra")) {
                    text = ""
                }
            }
        }
    }

    Rectangle {
        id: inputContainerRoomTypeIdUpdate
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
            id: fieldsRoomTypeIdUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Id typu pokoju")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Id typu pokoju")) {
                    text = ""
                }
            }
        }
    }

    Button {
        id: idButtonServTabUpdate
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerRoomNumberAdd.top
        anchors.topMargin: idInputTextContainerRoomNumberAdd.height * 0.08
        anchors.left: inputContainerRoomTypeIdAdd.right
        anchors.leftMargin: parent.width * 0.025

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
            radius: 15
        }

        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
            text: "Dodaj pokój"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");

            let errors = [];

            // Sprawdzenie pustych pól i ich poprawności
            if (!validateEmptyField(fieldsRoomNumberAdd.text)) {
                errors.push("Numer pokoju nie może być puste.");
            } else if (!validatePositiveInteger(fieldsRoomNumberAdd.text)) {
                errors.push("Numer pokoju musi być liczbą.");
            }

            if (!validateEmptyField(fieldsRoomFloorAdd.text)) {
                errors.push("Numer piętra nie może być puste.");
            } else if (!validateNumber(fieldsRoomFloorAdd.text)) {
                errors.push("Numer piętra musi być liczbą.");
            }

            if (!validateEmptyField(fieldsRoomTypeIdAdd.text)) {
                errors.push("Numer id pokoju nie może być puste.");
            } else if (!validatePositiveInteger(fieldsRoomTypeIdAdd.text)) {
                errors.push("Numer id pokoju musi być liczbą.");
            }

            // Jeśli są błędy walidacji
            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n")); // Wyświetl komunikaty błędów
            } else {
                // Wszystkie dane są poprawne - wysyłamy do backendu
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                bridgeRoom.addRoom(
                    fieldsRoomNumberAdd.text,
                    fieldsRoomFloorAdd.text,
                    fieldsRoomTypeIdAdd.text
                );
            }
        }
    }

    Rectangle {
        id: idInputTextContainerRoomNumberUpdate
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
            id: fieldsRoomNumberUpdate
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("Numer pokoju")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("Numer pokoju")) {
                    text = ""
                }
            }
        }
    }


    Button {
        id: idButtonRoomUpdate
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerRoomNumberUpdate.top
        anchors.topMargin: idInputTextContainerRoomNumberUpdate.height * 0.08
        anchors.left: idInputTextContainerRoomNumberUpdate.right
        anchors.leftMargin: parent.width * 0.025

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
            radius: 15
        }

        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
            text: "Aktualizuj pokój"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");

            let errors = [];

            // Sprawdzenie wymaganego pola ID pokoju
            if (!validateEmptyField(fieldsRoomIdUpdate.text)) {
                errors.push("ID pokoju nie może być puste.");
            } else if (!validatePositiveInteger(fieldsRoomIdUpdate.text)) {
                errors.push("ID pokoju musi być liczbą.");
            }

            // Pozostałe pola są opcjonalne - sprawdzamy tylko, jeśli użytkownik coś wpisał
            if (fieldsRoomNumberUpdate.text.length > 0 && !validatePositiveInteger(fieldsRoomNumberUpdate.text)) {
                errors.push("Numer pokoju musi być liczbą.");
            }

            if (fieldsRoomFloorUpdate.text.length > 0 && !validateNumber(fieldsRoomFloorUpdate.text)) {
                errors.push("Numer piętra musi być liczbą.");
            }

            if (fieldsRoomTypeIdUpdate.text.length > 0 && !validatePositiveInteger(fieldsRoomTypeIdUpdate.text)) {
                errors.push("ID typu pokoju musi być liczbą.");
            }

            // Jeśli są błędy walidacji
            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n"));
            } else {
                // Wszystkie dane są poprawne - wysyłamy do backendu
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                bridgeRoom.updateRoom(
                    parseInt(fieldsRoomIdUpdate.text, 10), // ID pokoju (wymagane)
                    fieldsRoomNumberUpdate.text.length > 0 ? parseInt(fieldsRoomNumberUpdate.text, 10) : null, // Numer pokoju (opcjonalne)
                    fieldsRoomFloorUpdate.text.length > 0 ? parseInt(fieldsRoomFloorUpdate.text, 10) : null, // Numer piętra (opcjonalne)
                    fieldsRoomTypeIdUpdate.text.length > 0 ? parseInt(fieldsRoomTypeIdUpdate.text, 10) : null // Typ pokoju (opcjonalne)
                );
            }
        }

    }


    Rectangle {
        id: idInputTextContainerIdRoomDel
        width: parent.width * 0.11
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
            id: fieldsIdRoomDel
            anchors.fill: parent
            color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
            text: qsTr("ID pokoju")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            selectionColor: "#ff0000"
            font.pixelSize: Math.min(dashboard.width * 0.013, dashboard.height * 0.1)
            clip: true // Maskowanie tekstu

            // Gdy TextInput dostaje focus i aktualny tekst to wciąż "Imię", to go czyścimy
            onActiveFocusChanged: {
                if (activeFocus && text === qsTr("ID pokoju")) {
                    text = ""
                }
            }
        }
    }

    Text {
        id: idTextDeleteRoom
        width: parent.width * 0.2 // 90% szerokości ramki
        height: parent.height * 0.05 // 10% wysokości ramki
        text: qsTr("Usuń pokój")
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

    Button {
        id: idButtonRoomDel
        width: parent.width * 0.1
        height: parent.height * 0.042

        anchors.top: idInputTextContainerIdRoomDel.top
        anchors.topMargin: idInputTextContainerIdRoomDel.height * 0.08
        anchors.left: idInputTextContainerIdRoomDel.right
        anchors.leftMargin: parent.width * 0.02

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#6aa84f" : "#ffe599"
            radius: 15
        }

        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000"
            text: "Usuń pokój"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            console.log("Przycisk został kliknięty.");

            let errors = [];

            // Sprawdzenie pustych pól i ich poprawności
            if (!validateEmptyField(fieldsIdRoomDel.text)) {
                errors.push("Id pokoju nie może być puste.");
            } else if (!validatePositiveInteger(fieldsIdRoomDel.text)) {
                errors.push("Id pokoju musi być liczbą.");
            }


            // Jeśli są błędy walidacji
            if (errors.length > 0) {
                console.log("Błędy walidacji:", errors);
                showValidationMessage(errors.join("\n")); // Wyświetl komunikaty błędów
            } else {
                // Wszystkie dane są poprawne - wysyłamy do backendu
                console.log("Wszystkie dane poprawne, wysyłanie do backendu...");

                bridgeRoom.deleteRoom(
                    fieldsIdRoomDel.text
                );
            }
        }
    }




}



