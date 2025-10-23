import QtQuick
import QtQuick.Controls

// Język QML - JavaScript


Item {
    id: root
    width: 1920
    height: 1080
    anchors.fill: parent

    Image {
        id: background
        source: "images/background_Log1_1920x1080.png"
        anchors.fill: parent
        anchors.leftMargin: 0
        anchors.rightMargin: 0
        anchors.topMargin: 0
        anchors.bottomMargin: 0
        fillMode: Image.PreserveAspectCrop
    }

    Text {
        id: info_logowanie
        text: qsTr("Aplikacja do zarządzania kliniką psychologiczno-psychiatryczną")
        font.pixelSize: Math.min(parent.width, parent.height) * 0.0512
        color: "#ffffff"
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: parent.width * 0.05 // 5% marginesu z lewej i prawej strony
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.15 // 5% marginesu od góry
        horizontalAlignment: Text.AlignHCenter // Wyrównanie wewnętrzne do środka
        wrapMode: Text.WordWrap // Automatyczne zawijanie tekstu
    }

    // Pole do wprowadzania imienia
    TextInput {
        id: usernameField
        width: parent.width * 0.3
        height: parent.height * 0.11
        font.pixelSize: Math.min(parent.width, parent.height) * 0.055
        color: "#22ff00"
        text: qsTr("Nazwa użytkownika")
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        selectionColor: "#ff0000"
        anchors.horizontalCenter: parent.horizontalCenter // Centruj w poziomie
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.3
    }

    TextInput {
        id: passwordField
        width: parent.width * 0.3
        height: parent.height * 0.11
        font.pixelSize: Math.min(parent.width, parent.height) * 0.055
        color: "#22ff00"
        text: qsTr("Hasło")
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        selectionColor: "#ff0000"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.45// Proporcjonalne pozycjonowanie
    }

        Text {
        id: errorMessage
        width: parent.width * 0.3
        height: parent.height * 0.11
        font.pixelSize: height * 0.32
        color: "#ff0000"
        visible: false
        horizontalAlignment: Text.AlignHCenter
        anchors.horizontalCenter: parent.horizontalCenter // Centruj w poziomie
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.58
    }

    Button {
        id: loginButton
        text: qsTr("Zaloguj")
        width: parent.width * 0.2
        height: parent.height * 0.07
        font.pixelSize: height * 0.4
        anchors.left: parent.left // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.leftMargin: parent.width * 0.2 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.2 // Margines od dolnej krawędzi (2% wy

        background: Rectangle {
        color: "#D3D3D3" // Szary kolor
        radius: 15 // Zaokrąglenie rogów o 5 pikseli
        }

        onClicked: {
            let result = backendBridge.login(usernameField.text, passwordField.text);
            if (result.startsWith("success")) {
                console.log("Logowanie zakonczone sukcesem:", result);
                errorMessage.visible = false;
                errorMessage.text = "";
            } else {
                console.error("Blad logowania:", result);
                errorMessage.visible = true;
                errorMessage.text = result.substring(6); // Usuń "error:" z wyniku
            }
        }
    }

    Button {
        id: exitButton
        text: qsTr("Wyjdź z aplikacji")
        width: parent.width * 0.2
        height: parent.height * 0.07
        font.pixelSize: height * 0.4
        anchors.right: parent.right // Kotwica do prawej krawędzi rodzica
        anchors.bottom: parent.bottom // Kotwica do dolnej krawędzi rodzica
        anchors.rightMargin: parent.width * 0.2 // Margines od prawej krawędzi (2% szerokości)
        anchors.bottomMargin: parent.height * 0.2 // Margines od dolnej krawędzi (2% wy

        background: Rectangle {
        color: "#D3D3D3" // Szary kolor
        radius: 15 // Zaokrąglenie rogów o 5 pikseli
        }
        // Obsługa kliknięcia
        onClicked: {
            Qt.quit(); // Wyłączenie aplikacji
        }
    }
}
