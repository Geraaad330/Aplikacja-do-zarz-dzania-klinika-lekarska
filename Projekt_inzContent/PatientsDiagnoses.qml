import QtQuick
import QtQuick.Controls

Rectangle {
    id: dashboard
    width: 1920
    height: 1080
    visible: true

    property bool isDarkMode: false

    Component.onCompleted: {
        console.log("Setting current screen to PatientsMainList");
        backendBridge.currentScreen = "PatientsMainList";
        backendBridge.updateDiagnosesDataForUserList(); // Wywołanie funkcji
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
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
    }

    Text {
        id: idBarHarmonogram
        width: idRamka.width * 0.9 // 90% szerokości ramki
        height: idRamka.height * 0.05 // 10% wysokości ramki
        text: qsTr("panel pacjenci")
        color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
        anchors.horizontalCenter: idRamka.horizontalCenter
        anchors.top: idRamka.top
        anchors.topMargin: idRamka.height * 0.065// Margines między tekstami
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        clip: true // Maskowanie tekstu
        font.pixelSize: Math.min(parent.width * 0.014, parent.height * 0.1)
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



    Text {
        text: qsTr("Panel pacjenci - lista diagnóz")
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



    Item {
        id: mainContainer       // Nadajemy id głównemu kontenerowi
        anchors.fill: parent

        // Definiujemy wspólne właściwości szerokości kolumn
        property real colWidthDiagId: 0.055
        property real colWidthAppId: 0.05
        property real colWidthName: 0.15
        property real colWidthStatus: 0.05
        property real colWidthDesc: 0.35
        property real colWidthIcd: 0.1

        Column {
            id: listContainer
            anchors {
                // left: idRamka.right
                right: parent.right
                top: parent.top
                bottom: parent.bottom
            }
            spacing: 5
            width: parent.width * 0.8
            height: parent.height * 0.8
            anchors.topMargin: parent.height * 0.14// 10% od góry
            anchors.leftMargin: parent.width * 0.04// 10% od lewej
            anchors.rightMargin: parent.width * 0.02  // opcjonalnie, dla zachowania odstępu od prawej
            anchors.bottomMargin: parent.height * 0.13

            // Nagłówek
            Row {
                id: headerRow
                width: listContainer.width
                height: listContainer.height * 0.08  // 8% wysokości kontenera
                spacing: 50

                Text {
                    text: "Id diagnozy"
                    width: headerRow.width * mainContainer.colWidthDiagId
                    // horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: 15
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    elide: Text.ElideRight
                }
                Text {
                    text: "Id wizyty"
                    width: headerRow.width * mainContainer.colWidthAppId
                    // horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: 15
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    elide: Text.ElideRight
                }
                Text {
                    text: "Imię i nazwisko"
                    width: headerRow.width * mainContainer.colWidthName
                    // horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: 17
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    elide: Text.ElideRight
                }
                Text {
                    text: "Status"
                    width: headerRow.width * mainContainer.colWidthStatus
                    // horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: 17
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    elide: Text.ElideRight
                }
                Text {
                    text: "Opis"
                    width: headerRow.width * mainContainer.colWidthDesc
                    // horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: 17
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    elide: Text.ElideRight
                }
                Text {
                    text: "Kod ICD-11"
                    width: headerRow.width * mainContainer.colWidthIcd
                    // horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: 17
                    color: backendBridge.isDarkMode ? "#FFFFFF" : "#ffde59"
                    elide: Text.ElideRight
                }
            }

            // ScrollView z listą
            ScrollView {
                id: idScrollView
                width: listContainer.width
                height: listContainer.height * 0.92  // pozostałe miejsce w kontenerze
                clip: true

                ListView {
                    id: diagnosesListView
                    anchors.fill: parent
                    model: diagnosesModel

                    delegate: Item {
                        width: diagnosesListView.width
                        height: 60   // Możesz ustawić wysokość na stałą lub proporcjonalną
                        Row {
                            spacing: 50
                            anchors.fill: parent

                            Text {
                                text: model.diagnosis_id
                                width: diagnosesListView.width * mainContainer.colWidthDiagId
                                font.pixelSize: 17            // Stała wielkość czcionki (nie skalująca się)
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                                color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap       // Tekst zawija się, gdy nie mieści się w zadanej szerokości
                                clip: true                   // Zapobiega wyświetlaniu tekstu poza obszarem
                                // Możesz ustawić maximumLineCount, np.:
                                maximumLineCount: 2
                                // elide: Text.ElideRight
                            }
                            Text {
                                text: model.fk_appointment_id
                                width: diagnosesListView.width * mainContainer.colWidthAppId
                                font.pixelSize: 17            // Stała wielkość czcionki (nie skalująca się)
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                                color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap       // Tekst zawija się, gdy nie mieści się w zadanej szerokości
                                clip: true                   // Zapobiega wyświetlaniu tekstu poza obszarem
                                // Możesz ustawić maximumLineCount, np.:
                                maximumLineCount: 2
                                // elide: Text.ElideRight
                            }
                            Text {
                                text: model.patient_name
                                width: diagnosesListView.width * mainContainer.colWidthName
                                font.pixelSize: 17           // Stała wielkość czcionki (nie skalująca się)
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                                color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap       // Tekst zawija się, gdy nie mieści się w zadanej szerokości
                                clip: true                   // Zapobiega wyświetlaniu tekstu poza obszarem
                                // Możesz ustawić maximumLineCount, np.:
                                maximumLineCount: 2
                                // elide: Text.ElideRight
                            }
                            Text {
                                text: model.is_active === 1 ? "Aktywny" : "Nie aktywny"  // Wyświetl "Tak" lub "Nie" zamiast 1/0
                                width: diagnosesListView.width * mainContainer.colWidthStatus
                                font.pixelSize: 17
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                                color: backendBridge.isDarkMode ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap
                                clip: true
                                maximumLineCount: 2
                            }
                            Text {
                                text: model.description
                                width: diagnosesListView.width * mainContainer.colWidthDesc
                                font.pixelSize: 17           // Stała wielkość czcionki (nie skalująca się)
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                                color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap       // Tekst zawija się, gdy nie mieści się w zadanej szerokości
                                clip: true                   // Zapobiega wyświetlaniu tekstu poza obszarem
                                // Możesz ustawić maximumLineCount, np.:
                                maximumLineCount: 2
                                // elide: Text.ElideRight

                            }
                            Text {
                                text: model.icd11_code
                                width: diagnosesListView.width * mainContainer.colWidthIcd
                                font.pixelSize: 17            // Stała wielkość czcionki (nie skalująca się)
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                                color: (backendBridge && backendBridge.isDarkMode) ? "#ff0000" : "#FFFFFF"
                                wrapMode: Text.WordWrap       // Tekst zawija się, gdy nie mieści się w zadanej szerokości
                                clip: true                   // Zapobiega wyświetlaniu tekstu poza obszarem
                                // Możesz ustawić maximumLineCount, np.:
                                maximumLineCount: 2
                                // elide: Text.ElideRight
                            }
                        }
                    }
                }
            }

            ListModel {
                id: diagnosesModel
            }

            // Obsługa pobranych danych
            Connections {
                target: backendBridge
                function onMedicalDataFetched(data) {
                    diagnosesModel.clear();
                    for (let record of data.records) {
                        // Sprawdzenie i uzupełnienie brakujących danych
                        for (let key in record) {
                            if (record[key] === undefined || record[key] === null) {
                                record[key] = "Brak danych";
                            }
                        }
                        diagnosesModel.append(record);
                    }
                }
            }
        }
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
        id: idPatientsDiagnoses
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.45 // Margines od dolnej krawędzi (2% wy

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
            text: "Zarządzanie diagnozami"
            font.pixelSize: Math.min(parent.width * 0.075, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "PatientsDiagnosesCRUD.qml";
            // Zmieniamy stan isClicked na true

        }

    }


    Button {
        id: idPatientsMedicalData
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.55 // Margines od dolnej krawędzi (2% wy

        // Właściwość do przechowywania stanu kliknięcia
        property bool isClicked: false

        // Tło przycisku z dynamiczną zmianą kolorów

        background: Rectangle {
            color: backendBridge.currentScreen === "PatientsMainList"
                   ? "#6aa84f" // Kolor dla aktywnego przycisku "#A9A9A9"
                   : backendBridge.isDarkMode ? "#961c3d" : "#ffe599" // Tryb ciemny/jasny
            radius: 15
        }

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Lista diagnóz"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            mainViewLoader.source = "PatientsDiagnoses.qml";
            // Zmieniamy stan isClicked na true
            idPatientsMainList.isClicked = true;
        }

    }


    Button {
        id: idPatientsMainList
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
            text: "Lista pacjentów"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // backendBridge.currentScreen = "PatientsMainList"; // Zmiana aktywnej zakładki
            // Przełącz widok na Login.qml
            mainViewLoader.source = "PatientsMainList.qml";

        }


    }

    Button {
        id: idPatientsCRUD
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.65 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Zarządzanie pacjentami"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.32)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }


        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "PatientsCRUD.qml";


        }


        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }

    }



    Button {
        id: idPatientsPerscriptionsCRUD
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.25 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Zarządzanie receptami"
            font.pixelSize: Math.min(parent.width * 0.08, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "PatientsPrescriptionsCRUD.qml";
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }
    }

    Button {
        id: idPatientsPerscriptions
        width: parent.width * 0.1
        height: parent.height * 0.042
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.018 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.35 // Margines od dolnej krawędzi (2% wy

        // Zmiana koloru tekstu w zależności od trybu
        contentItem: Text {
            color: backendBridge.isDarkMode ? "#FFFFFF" : "#000000" // Biały tekst w trybie ciemnym, czarny w trybie jasnym
            text: "Lista Recept"
            font.pixelSize: Math.min(parent.width * 0.1, parent.height * 0.5)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            // Przełącz widok na Login.qml
            mainViewLoader.source = "PatientsPrescriptions.qml";
        }

        background: Rectangle {
            color: backendBridge.isDarkMode ? "#961c3d" : "#ffe599"  // Ciemny kolor w trybie ciemnym, jasny w trybie jasnym
            radius: 15 // Zaokrąglenie rogów o 15 pikseli
        }
    }

}

