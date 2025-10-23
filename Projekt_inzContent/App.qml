// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.Controls
//import Projekt_inz

Window {
    id: mainWindow
    width: 1920
    height: 1080
    visible: true
    title: qsTr("Aplikacja do zarządzania kliniką lekarską - projekt inżynierski")  // Tytuł w pasku okna
    flags: Qt.Window  // Domyślny styl okna z paskiem tytułu
    // Ustawienie stylu Material
    //Control.style: "Material"


    // Główny loader do zarządzania widokami
    Loader {
        id: mainViewLoader
        anchors.fill: parent
        source: "Login.qml" // Startowy plik QML
        onSourceChanged: console.log("Loader source zmieniony na: " + source)
    }


    Connections {
        target: backendBridge

        function onLoginSuccess(username, role) {
            console.log("Przelaczanie widoku...");
            console.log("Logowanie zakonczone sukcesem: " + username + " (" + role + ")");
            mainViewLoader.source = "Dashboard.qml";
        }

        function onLoginFailure(message) {
            console.error("Blad logowania: " + message);
        }

    }

    Component.onCompleted: {
        console.log("App.qml załadowane");
        console.log("backendBridge.isDarkMode:", backendBridge.isDarkMode);
    }

}

