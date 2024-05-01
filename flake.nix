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
            pkgs = nixpkgs.legacyPackages.${system}.extend
              (final: prev: {
                git-archive-all = prev.git-archive-all.overrideAttrs (
                  finalAttrs: oldAttrs: {
                    src = prev.fetchFromGitHub {
                      owner = "NMaghfurUsman";
                      repo = "git-archive-all";
                      rev = "master";
                      hash = "sha256-sRqy9AayLa4Xv2316kWhgyuX+47YZFU0oZ+xZFT6qCI=";
                      };
                    }
                  );
                }
            ) ;
          in
          {
            default = devenv.lib.mkShell {
              inherit inputs pkgs;
              modules = [
                {
                  # https://devenv.sh/reference/options/
                  packages = with pkgs; [ 
                    python3Packages.pyqt5 
                    python3Packages.pyqt5-stubs 
                    git-archive-all];
                  processes = {
                        client.exec = "python -m http.server -d ./krita_remote/client";
                  };
                  scripts = {
                        build-plugin.exec = "git-archive-all -D krita_remote.zip";
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
