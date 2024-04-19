{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    systems.url = "github:nix-systems/default";
    devenv.url = "github:cachix/devenv";
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = { self, nixpkgs, devenv, systems, ... } @ inputs:
    let
      forEachSystem = nixpkgs.lib.genAttrs (import systems);
    in
    {
      packages = forEachSystem (system: {
        devenv-up = self.devShells.${system}.default.config.procfileScript;
      });

      devShells = forEachSystem
        (system:
          let
            pkgs = nixpkgs.legacyPackages.${system}.extend (import ./pyqt5-qtwebsockets.nix);
          in
          {
            default = devenv.lib.mkShell {
              inherit inputs pkgs;
              modules = [
                {
                  # https://devenv.sh/reference/options/
                  packages = [ pkgs.krita pkgs.python3Packages.pyqt5 pkgs.python3Packages.pyqt5-stubs pkgs.python3Packages.pyqt5-sip];
                  processes = {
                        client.exec = "python -m http.server -d ./krita_remote/client";
                  };
                  env.PYTHONPATH = "${pkgs.python3Packages.pyqt5}/lib/python3.11/site-packages/";
                  enterShell = ''
                    echo "Dev Shell for Krita Remote"
                    echo "\$PYTHONPATH=$PYTHONPATH"
                  '';

                }
              ];
            };
          });
    };
}
