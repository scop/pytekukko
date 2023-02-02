"""Pytekukko examples."""

import os
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional

from aiohttp import ClientSession, CookieJar
from dotenv import find_dotenv, load_dotenv

from pytekukko import Pytekukko


def arg_environ_default(
    key: str,
    *,
    optional: bool = False,
    fallback: Optional[str] = None,
) -> dict[str, Optional[str]]:
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


def example_argparser(description: str) -> ArgumentParser:
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
    argparser.add_argument(
        "--customer-number",
        type=str,
        **arg_environ_default("PYTEKUKKO_CUSTOMER_NUMBER"),  # type: ignore[arg-type]
    )
    argparser.add_argument(
        "--password",
        type=str,
        **arg_environ_default("PYTEKUKKO_PASSWORD"),  # type: ignore[arg-type]
    )
    argparser.add_argument(
        "--cookie-jar-file",
        type=str,
        **arg_environ_default(  # type: ignore[arg-type]
            "PYTEKUKKO_COOKIE_JAR_FILE",
            optional=True,
        ),
    )

    return argparser


def example_client(args: Namespace) -> tuple[Pytekukko, CookieJar, Optional[Path]]:
    """Set up example client."""
    if not args.customer_number:
        print("customer number required", file=sys.stderr)  # noqa: T201
        sys.exit(2)
    if not args.password:
        print("password required", file=sys.stderr)  # noqa: T201
        sys.exit(2)
    cookie_jar = CookieJar()
    cookie_jar_path = None
    if args.cookie_jar_file:
        cookie_jar_path = Path(args.cookie_jar_file)
        if cookie_jar_path.exists():
            cookie_jar.load(cookie_jar_path)

    client = Pytekukko(
        session=ClientSession(cookie_jar=cookie_jar),
        customer_number=args.customer_number,
        password=args.password,
    )

    return client, cookie_jar, cookie_jar_path
