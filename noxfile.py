"""nox config for pytekukko."""

# Copyright 2023 Ville Skyttä

import nox

nox.options.error_on_external_run = True


@nox.session(
    python=[f"3.{x}" for x in range(10, 16)] + [f"pypy3.{x}" for x in range(11, 12)]
)
def test(session: nox.Session) -> None:
    """Run tests."""
    session.install(".[examples]", "-r", "requirements/test-requirements.txt")

    known_deprecations = [
        "-W",
        (  # https://github.com/pytest-dev/pytest-asyncio/issues/1025
            r"default:'asyncio.get_event_loop_policy':"
            "DeprecationWarning:pytest_asyncio.plugin"
        ),
        "-W",
        (  # https://github.com/pytest-dev/pytest-asyncio/issues/1025
            r"default:'asyncio.set_event_loop_policy':"
            "DeprecationWarning:pytest_asyncio.plugin"
        ),
        "-W",
        (  # https://github.com/aio-libs/aiohttp/pull/7302, included in aiohttp >= 3.9
            "default:datetime.datetime.utcfromtimestamp:"
            "DeprecationWarning:aiohttp.cookiejar"
        ),
        "-W",
        (  # aiohttp 3.8.6 in -X dev mode
            "default:"
            "Setting custom ClientSession._resolve_charset attribute is discouraged:"
            "DeprecationWarning:aiohttp.client"
        ),
        "-W",
        (  # https://github.com/dateutil/dateutil/pull/1285, dateutil <= 2.8.2
            "default:datetime.datetime.utcfromtimestamp:"
            "DeprecationWarning:dateutil.tz.tz"
        ),
    ]

    cmd = ["python3", "-X", "dev", "-bb"]
    session.run(*cmd, "-m", "pytest", *known_deprecations, *session.posargs)

    cmd += ["-W", "error", *known_deprecations, "-m"]
    session.run(
        *cmd,
        "pytekukko.examples.print_invoices",
        "--help",
        silent=True,
    )
    session.run(
        *cmd,
        "pytekukko.examples.print_next_emptyings",
        "--help",
        silent=True,
    )
    session.run(
        *cmd,
        "pytekukko.examples.print_planned_emptyings",
        "--help",
        silent=True,
    )

    session.run(
        "shtab",
        "--prog",
        "pytekukko-invoices",
        "--prefix",
        "pytekukko_invoices",
        "pytekukko.examples.print_invoices.argparser",
        silent=True,
    )
    session.run(
        "shtab",
        "--prog",
        "pytekukko-next-emptyings",
        "--prefix",
        "pytekukko_next_emptyings",
        "pytekukko.examples.print_next_emptyings.argparser",
        silent=True,
    )
    session.run(
        "shtab",
        "--prog",
        "pytekukko-planned-emptyings",
        "--prefix",
        "pytekukko_planned_emptyings",
        "pytekukko.examples.pytekukko_planned_emptyings.argparser",
        silent=True,
    )
