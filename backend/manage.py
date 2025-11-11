#!/usr/bin/env python3
"""Management CLI for the backend.

Provides a small Click-based wrapper around Alembic for local development.

Commands:
  upgrade [rev]        Run alembic upgrade (default: head)
  downgrade <rev>      Run alembic downgrade to specified revision
  revision             Create a new autogenerate revision (passes -m and --autogenerate)
  current              Show current revision
  history              Show revision history
"""
import os
import shlex
import subprocess
import sys
from pathlib import Path

import click

REPO_ROOT = Path(__file__).resolve().parent.parent
ALEMBIC_INI = REPO_ROOT / "alembic.ini"


def _run_alembic(args: str):
    cmd = [sys.executable, "-m", "alembic"] + shlex.split(args)
    click.echo("Running: %s" % (" ".join(cmd)))
    subprocess.run(cmd, check=True, cwd=str(REPO_ROOT))


@click.group()
def cli():
    """Simple manage CLI for the backend."""


@cli.command()
@click.argument('rev', required=False, default='head')
def upgrade(rev):
    """Upgrade the DB to REV (default: head)."""
    _run_alembic(f"-c {ALEMBIC_INI} upgrade {rev}")


@cli.command()
@click.argument('rev', required=True)
def downgrade(rev):
    """Downgrade the DB to REV."""
    _run_alembic(f"-c {ALEMBIC_INI} downgrade {rev}")


@cli.command()
@click.option('--message', '-m', required=True, help='Revision message')
@click.option('--autogenerate', is_flag=True, default=False, help='Run alembic --autogenerate')
def revision(message, autogenerate):
    """Create a new migration revision."""
    auto = '--autogenerate' if autogenerate else ''
    _run_alembic(f"-c {ALEMBIC_INI} revision {auto} -m \"{message}\"")


@cli.command()
def current():
    """Show current revision."""
    _run_alembic(f"-c {ALEMBIC_INI} current")


@cli.command()
def history():
    """Show revision history."""
    _run_alembic(f"-c {ALEMBIC_INI} history")


if __name__ == '__main__':
    cli()
