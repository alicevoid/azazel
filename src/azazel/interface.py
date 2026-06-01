"""
Interface Design

    CLI integration

"""

import click
import os
import logging
from azazel.server import FTPServer
from azazel.client import FTPClient
from azazel.log import get_logger

# TODO: add help flags to everything


@click.group()
def cli():
    pass


@cli.command()
@click.option("--port", default=2121, help="Port to listen on (default: 2121)")
@click.option(
    "--root",
    default=os.getcwd(),
    help="Root directory to serve (default: current directory)",
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Displays INFO and DEBUG info directly in the console",
)
def server(port, root, verbose):
    if verbose:
        logger = get_logger()
        get_logger().setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)

    click.echo(f"starting server on port {port}, serving {root}")
    ftp = FTPServer(port=port, root=root)
    ftp.start()
    pass


@cli.command()
@click.option("--host", default="localhost")
@click.option("--port", default=2121)
@click.option("--user", default="anonymous")
@click.option("--password", default="")
def client(host, port, user, password):
    c = FTPClient(host, port)
    c.connect()
    c.login(user, password)


@cli.command()
def log():
    log_path = os.path.join(
        os.path.expanduser("~"), ".local", "share", "azazel", "azazel.log"
    )
    with open(log_path) as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if line:
                click.echo(line, nl=False)
