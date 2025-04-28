# pytekukko -- Jätekukko Omakukko API client

[![Python versions](https://img.shields.io/pypi/pyversions/pytekukko.svg)](https://pypi.org/project/pytekukko/)
[![PyPI version](https://badge.fury.io/py/pytekukko.svg)](https://badge.fury.io/py/pytekukko)
[![CI status](https://github.com/scop/pytekukko/workflows/check/badge.svg)](https://github.com/scop/pytekukko/actions?query=workflow%3Acheck)

Simple asyncio client for the [Jätekukko](https://www.jatekukko.fi)
[Omakukko](https://tilasto.jatekukko.fi/indexservice2.jsp) API.

The API of this package is modeled closely after the Omakukko
API. Only read operations are implemented (well apart from, strictly
speaking, login/logout), and there are no plans to add support for any
write ones.

Usage in a nutshell:

- construct an aiohttp [`ClientSession`](https://docs.aiohttp.org/en/stable/client_reference.html#client-session),
- construct a `Pytekukko` client with it and your credentials,
- invoke methods on the client.

The Omakukko API uses cookie based sessions, use a persistent aiohttp
[`CookieJar`](https://docs.aiohttp.org/en/stable/client_reference.html#cookiejar)
to maintain client session across interpreter restarts.

High level client methods handle logging in when the need to do so is
detected. If the detection is successful, there is no need to
separately track session expiration or use the `login` method in the
first place.

For usage examples, see utilities in the `pytekukko.examples`
package. Executables and dependencies for these are installed when the
package is installed with the `examples` extra, invoke them with
`--help` for usage and setup information:

- `pytekukko-collection-schedules`: output collection schedules in JSON
- `pytekukko-invoice-headers`: output basic info on invoices in JSON
- `pytekukko-next-collections`: output next collection dates in JSON

## Disclaimer

This package is not supported by or endorsed by Jätekukko. Do not
bother them with questions or issues related to it.
