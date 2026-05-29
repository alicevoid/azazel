"""
Interface Design

    CLI integration

"""

import click
import os 

@click.command()
@click.option('--port', default=2121, help='Port to listen on (default: 2121)')
@click.option('--root', default=os.getcwd(), help='Root directory to serve (default: current directory)')
