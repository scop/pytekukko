#!/usr/bin/env python3

"""Print basic info on invoices."""

import asyncio
import json

from pytekukko.examples import example_argparser, example_client


async def run_example() -> None:
    """Run the example."""
    client, cookie_jar, cookie_jar_path = example_client(
        example_argparser(__doc__).parse_args(),
    )

    async with client.session:
        data = [
            {
                "name": invoice_header.name,
                "due_date": invoice_header.due_date.isoformat(),
                "total": invoice_header.total,
            }
            for invoice_header in await client.get_invoice_headers()
        ]
        if not cookie_jar_path:
            await client.logout()

    print(json.dumps(data))  # noqa: T201

    if cookie_jar_path:
        cookie_jar.save(cookie_jar_path)


def main() -> None:
    """Run example in event loop."""
    asyncio.run(run_example())


if __name__ == "__main__":
    main()
