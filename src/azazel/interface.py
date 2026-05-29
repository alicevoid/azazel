"""
Interface Design

    CLI integration

"""

import click
import os
from azazel.server import FTPServer


@click.command()
@click.option("--port", default=2121, help="Port to listen on (default: 2121)")
@click.option(
    "--root",
    default=os.getcwd(),
    help="Root directory to serve (default: current directory)",
)
def main(port, root):
    click.echo(f"starting azazel on port {port}, with root {root}")
    ftp = FTPServer(host="", port=port, root=root)
    ftp.start()
