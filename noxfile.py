"""nox config for pytekukko."""

import nox

nox.options.error_on_external_run = True


@nox.session(python=[f"{py}3.{x}" for py in ("", "pypy") for x in range(9, 13)])
def test(session: nox.Session) -> None:
    """Run tests."""
    session.install(".[examples]", "-r", "requirements/test-requirements.txt")

    prefix = "python3 -X dev -bb"
    session.run(*f"{prefix} -m pytest".split() + session.posargs)

    prefix += " -W error"
    # https://github.com/aio-libs/aiohttp/pull/7302
    prefix += (
        " -W default:datetime.utcfromtimestamp:DeprecationWarning:aiohttp.cookiejar"
    )
    prefix += " -m pytekukko.examples"
    session.run(*f"{prefix}.print_collection_schedules --help".split(), silent=True)
    session.run(*f"{prefix}.print_invoice_headers --help".split(), silent=True)
    session.run(*f"{prefix}.print_next_collections --help".split(), silent=True)
    session.run(*f"{prefix}.update_google_calendar --help".split(), silent=True)
