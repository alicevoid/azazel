{
  description = "azazel - a command-line FTP server";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;
      in {
        packages.default = python.pkgs.buildPythonApplication {
          pname = "azazel";
          version = "0.1.0";
          src = ./.;
          pyproject = true;

          build-system = with python.pkgs; [
            setuptools
          ];

          dependencies = with python.pkgs; [
            click
          ];
        };

        devShells.default = pkgs.mkShell {
          packages = [
            python
            python.pkgs.click
            python.pkgs.coverage
          ];
        };
      }
    );
}
