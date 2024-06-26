# Krita Remote

Krita Remote is a Python extension that allows Krita to be remotely controlled over a WebSockets connection.

![Krita Remote webapp and Krita Remote docker](docker_screenshot.png)

This extension also supplies a webapp to use on your phone. By performing directional flick gestures on the webapp, you can remotely control Krita via the Krita Remote extension, and trigger actions such as Undo, Copy/Paste, switching to Brush, Eraser, resizing brush, etc. Even keyboard keys like Shift, Ctrl can be triggered. The webapp is designed with large target areas, so that very specific gestures can be performed accurately without your direct line-of-sight to the touchscreen.

## Installation

1. Open Krita.

2. Go to *Tools* -> *Scripts* -> *Import Python Plugin from Web*

3. A dialog will pop up. Copy this link into the input https://github.com/NMaghfurUsman/kra-remote/releases/download/v0.1/kra-remote-v0.1.zip

   Press OK.

4. Restart Krita.

5. Enable the docker in *Settings* -> *Dockers* -> *Krita Remote*

## Usage

The WebSockets connection is initiated through the Krita Remote docker, press the Connect button to start it and display a QR code to scan with your phone to open the client.

> [!WARNING]
> Transport Layer Security is unsupported, don't scan the QR code on untrusted WiFi (such as public WiFi access points).

The Krita Remote docker also displays an event log.

## Client

The client (ie, the remote control) is a simple Vue webapp that is served using Python's built-in HTTP server, which is also started in Krita by the Python extension. The Vue webapp uses a modified version of [vue3-touch-events](https://github.com/robinrodricks/vue3-touch-events) for detecting touchscreen gestures and triggering actions in Krita.

 - tap
 - drag
 - press
 - release
 - swipe (orthogonal and diagonal directions)
 - flick (orthogonal and diagonal directions), this is a directional swipe gesture that is followed immediately by swiping back to where you started, without releasing your finger.

I have added basic multi-touch gestures, so a different action is triggered for touch gestures that are performed with more than one finger (it only distinguishes multi-finger gestures from single-finger gestures, so using 2 or more fingers will trigger the same action. 3-finger and 4-finger gestures are typically reserved for the operating system's own use)

 - multitap
 - multipress
 - multirelease
 - multiswipe
 - multiflick
 - TODO: multidrag

 This client is just an experimental proof-of-concept. It doesn't even have to be a webapp, anything that can connect to WebSockets are just as capable.

 It is not customizable yet, but if you really want to change the actions then just edit the`index.html` file.

 ## WebSockets Server

 The server is a WebSockets server that runs in Krita in the Python Extension object. It listens for messages sent to the socket in the format `<type>:<value>`. The following messages are supported:

 - `action:<Krita action name>`, eg `action:edit_undo` will trigger the Undo action
 - `action:tool:<Krita tool name>`, eg `action:tool:KritaShape/KisToolBrush` will activate the Freehand Brush Tool
 - `press:<Qt key name>`, eg `press:Key_Space` will inject a Space press event in the current canvas
 - `release:<Qt key name`, eg `press:Key_Space` will inject a Space release event in the current canvas

WebSockets is a two-way communication protocol, however this extension only listens for messages. Nothing is sent back to the remote.

> [!WARNING]
> Transport Layer Security is unsupported, don't run the WebSockets server on untrusted WiFi.

## Note

I'm not proficient in the conventions for developing in Python nor Qt, much less PyQt5, but I'm open to learning more. Please teach me!

## Acknowledgements

Thank you wojtryb for publishing a [Python Krita API wrapper with typing](https://github.com/wojtryb/Shortcut-Composer/tree/main/shortcut_composer/api_krita)

Thank you robrodricks for the easy-to-use and easy-to-modify [vue3-touch-events](https://github.com/robinrodricks/vue3-touch-events) Vue plugin. Without your work, I would not have bothered developing this Krita extension.