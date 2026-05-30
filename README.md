# azazel

An oddly-demonic FTP server built in Python designed for the command line. Designed first and foremost for NixOS. 

-----
# installation 

### with flakes

in your flake:

```nix
inputs.azazel.url = "github:alicevoid/azazel";
```
in your packages:

```nix
environment.systemPackages = [
  inputs.azazel.packages.${system}.default
];
```

### with nix-shell

```bash
git clone https://github.com/alicevoid/azazel
cd azazel
nix-shell
pip install -e .
```

-----
# Usage 

```bash
# serve current directory on default port 2121
azazel

# specify port and root directory
azazel --port 2121 --root ./myfiles
```

Currently, this is about the extent of what you can do with it through the command line. This project is an early work in progress (see roadmap for current status), and this will be updated with a more thorough list of commands as they're implemented. 

## roadmap

- [x] control connection + command dispatch
- [x] USER/PASS authentication
- [x] directory navigation (CWD, PWD)
- [x] directory listing (LIST)
- [x] file transfer (RETR, STOR)
- [x] active mode (PORT)
- [x] passive mode (PASV)
- [x] CLI entry point 
- [x] NixOS flake packaging
- [x] logging
- [ ] proper authentication methods
- [ ] FTPS — TLS support
- [ ] internet deployment (NAT traversal, DDNS)
- [ ] extended CLI subcommands

-----
# etc...
This project is licensed under the GPL-3.0 License.

100% artisan-made code by hand.

alicevoid - make sure to love yourself <3
