# Krita Remote

Krita Remote is a Python extension that allows Krita to be remotely controlled over a network connection. It does this by exposing the Krita API as a WebSockets server using PyQt5's QtWebSockets library.

The PyQt5 version that is included in the official Krita appimage does not come with QtWebSockets, so the Krita distribution that is in nixpkgs is used instead, and can be accessed in this repository's flake.nix devShell. A Nix overlay is applied so that QtWebSockets is available with PyQt5
