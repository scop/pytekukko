"""Pytekukko examples."""

# Copyright 2021 Ville Skyttä

import json
import os
import sys
from argparse import ArgumentParser, Namespace
from datetime import datetime
from pathlib import Path

from aiohttp import ClientSession
from dotenv import find_dotenv, load_dotenv

from pytekukko import Pytekukko
from pytekukko.models import TokenInfo


def arg_environ_default(
    key: str,
    *,
    optional: bool = False,
    fallback: str | None = None,
) -> dict[str, str | None]:
    """Get kwargs for environment backed argument addition."""
    help_text = f"default: ${key} from environment"
    if optional:
        help_text += " (optional)"
    if fallback:
        help_text += f", or {fallback}"
    return {
        "default": os.environ.get(key, fallback),
        "help": help_text,
    }


def load_pytekukko_dotenv() -> bool:
    """Load our .env."""
    return load_dotenv(os.environ.get("PYTEKUKKO_DOTENV", find_dotenv(usecwd=True)))


def example_argparser(description: str | None) -> ArgumentParser:
    """Set up example argument parser."""
    _ = load_pytekukko_dotenv()

    argparser = ArgumentParser(
        description=description,
        epilog=(
            "Environment variable defaults are loaded from the path set in "
            "$PYTEKUKKO_DOTENV in environment, falling back to .env if not set. "
            "If the path is relative, it is searched in directories starting from the "
            "current directory, walking towards the file system root."
        ),
    )
    _ = argparser.add_argument(
        "--username",
        type=str,
        **arg_environ_default("PYTEKUKKO_USERNAME"),  # type: ignore[arg-type]
    )
    _ = argparser.add_argument(
        "--password",
        type=str,
        **arg_environ_default("PYTEKUKKO_PASSWORD"),  # type: ignore[arg-type]
    )
    _ = argparser.add_argument(
        "--token-file",
        type=str,
        **arg_environ_default(  # type: ignore[arg-type]
            "PYTEKUKKO_TOKEN_FILE",
            optional=True,
        ),
    )

    return argparser


def load_token(path: Path) -> TokenInfo | None:
    """Load a token from a file saved with :func:`save_token`."""
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return TokenInfo(
        token=data["token"],
        expires_at=datetime.fromisoformat(data["expires_at"]),
    )


def save_token(token: TokenInfo | None, path: Path) -> None:
    """Save a token to a file, or remove the file if there is no token."""
    if token is None:
        path.unlink(missing_ok=True)
        return
    data = {"token": token.token, "expires_at": token.expires_at.isoformat()}
    path.touch(mode=0o600)
    _ = path.write_text(json.dumps(data))


def example_client(args: Namespace) -> tuple[Pytekukko, Path | None]:
    """Set up example client."""
    if not args.username:
        print("username required", file=sys.stderr)  # noqa: T201
        sys.exit(2)
    if not args.password:
        print("password required", file=sys.stderr)  # noqa: T201
        sys.exit(2)
    token_path = Path(args.token_file) if args.token_file else None

    client = Pytekukko(
        session=ClientSession(),
        username=args.username,
        password=args.password,
        token=load_token(token_path) if token_path else None,
    )

    return client, token_path
