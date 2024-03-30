# Krita Remote

Krita Remote is a Python extension that allows Krita to be remotely controlled over a network connection. It does this by exposing the Krita API as a WebSockets server using PyQt5's QtWebSockets library.

The PyQt5 version that is included in the official Krita appimage does not come with QtWebSockets, so the Krita distribution that is in nixpkgs is used instead, and can be accessed in this repository's flake.nix devShell. A Nix overlay is applied so that QtWebSockets is available with PyQt5

![Krita Remote docker](screenshot.png)

## Usage

You need ``nix`` (with flakes enabled) to build a version of the ``nixpkgs`` distribution of Krita, but with QtWebSockets. This will happen automatically when entering the devShell:

```
$ nix develop --impure
```

Copy ``krita_remote.desktop`` file and the ``krita_remote`` folder to your Krita python plugin folder.

Run the proof-of-concept remote web UI server in a separate terminal and navigate to it in your browser:

```
$ python -m http.server -d ./client
```

Run Krita, (probably with [nixGL](https://github.com/nix-community/nixGL), though in some situations it is not necessary)

```
$ nixGL krita
```

The WebSocket server is controlled in the Krita Remote docker, press the start button to start it, and then copy-paste the address displayed in the docker into the remote web UI (tap anywhere on the UI to open the connection dialog)

## Client

The client (ie, the remote control) is a simple hacked-together static HTML/JS webapp with no build step, to be displayed on a smartphone. It uses vue3-touch-inputs for easily binding handlers to a variety of touchscreen gestures:

 - tap
 - drag
 - press
 - release
 - swipe (top/bottom/left/right)
 - flick (top/bottom/left/right)

I have added rudimentary multi-touch varieties, so different handlers can be triggered for touch gestures that are performed with more than one finger:

 - multitap
 - multipress
 - multirelease
 - TODO: multidrag
 - TODO: multiswipe
 - TODO: multiflick

 This client is just an experimental proof-of-concept. It doesn't even have to be a webapp, anything that can behave as a WebSockets client is just as capable. I'm even thinking of using a game engine like Godot and its touch UI library (I have almost zero experience developing for mobile).

 ## Server

 The server is a WebSockets server that runs in the Krita python extension. It listens for messages from the remote in the format `<type>:<value>` to invoke behaviour in Krita

 - `action:<Krita action name>`, eg `action:edit_undo` will trigger the Undo action
 - `press:<Qt key name>`, eg `press:Key_Space` will inject a Space press event in the current canvas
 - `release:<Qt key name`, eg `press:Key_Space` will inject a Space release event in the current canvas

 All WebSockets communication is sent from client to server, like an actual TV remote control (🤷 I've never heard of a TV that sends a reply back to a remote, nor a remote that can display anything). But this is all just software at the end of the day, so anything is possible I suppose!

## Note

I'm not proficient in the conventions for developing in Python nor Qt, much less PyQt5. Please teach me!

## Acknowledgements

Thank you wojtryb for publishing a [Python Krita API wrapper with typing](https://github.com/wojtryb/Shortcut-Composer/tree/main/shortcut_composer/api_krita)

Thank you robrodricks for the easy-to-use [vue3-touch-events](https://github.com/robinrodricks/vue3-touch-events) plugin