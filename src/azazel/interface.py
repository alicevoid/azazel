"""
Interface Design

    CLI integration

"""

import click
import os
import logging
import secrets
from azazel.server import FTPServer
from azazel.client import FTPClient
from azazel.log import get_logger

# TODO: add help flags to everything


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--fff",
    is_flag=True,
    default=False,
)
@click.option(
    "--port",
    default=2121,
    help="Port to listen on (default: 2121)",
)
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

    if fff:
        # TODO: did we specify filenames? if so, we only host a subset of them

        # creates passphrase
        fff_pass = secrets.token_urlsafe(21)

        # picks the root and port for you

        # creates the fff session
        click.echo(f"fff-code: 127.0.0.1:{port}:{fff_pass}")
        ftp = FTPSession(port=port, root=os.getcwd(), fff_pw=self.fff_pw)
        ftp.start()

    else:
        click.echo(f"starting server on port {port}, serving {root}")
        ftp = FTPServer(port=port, root=root)
        ftp.start()


@cli.command()
@click.option(
    "--fff",
    default=None,
)
@click.option(
    "--host",
    default="localhost",
)
@click.option(
    "--port",
    default=2121,
)
@click.option(
    "--user",
    default="anonymous",
)
@click.option(
    "--password",
    default="",
)
def client(host, port, user, password):
    if fff:
        # send the password
        # get told if we got it right
        # start pulling everything
        pass

    else:
        c = FTPClient(host, port)
        c.connect()
        c.login(user, password)
        # pull everything


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


# helper:
