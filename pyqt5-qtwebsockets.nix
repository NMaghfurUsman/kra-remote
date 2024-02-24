    final: prev: {
    python3Packages = prev.python3Packages.overrideScope (pfinal: pprev: {
      pyqt5 = pprev.pyqt5.override { withWebSockets=true;}
      ;});}

