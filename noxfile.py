"""nox config for pytekukko."""

import nox

nox.options.error_on_external_run = True


@nox.session(python=[f"{py}3.{x}" for py in ("", "pypy") for x in range(10, 15)])
def test(session: nox.Session) -> None:
    """Run tests."""
    session.install(".[examples]", "-r", "requirements/test-requirements.txt")

    known_deprecations = [
        "-W",
        (  # https://github.com/pytest-dev/pytest-asyncio/issues/929, slated for 1.0
            "default:'asyncio.iscoroutinefunction':"
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
        "pytekukko.examples.print_collection_schedules",
        "--help",
        silent=True,
    )
    session.run(
        *cmd,
        "pytekukko.examples.print_invoice_headers",
        "--help",
        silent=True,
    )
    session.run(
        *cmd,
        "pytekukko.examples.print_next_collections",
        "--help",
        silent=True,
    )
    session.run(
        *cmd,
        "pytekukko.examples.update_google_calendar",
        "--help",
        silent=True,
    )
