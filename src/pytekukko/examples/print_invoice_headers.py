#!/usr/bin/env python3

# Copyright 2021 Ville Skyttä

"""Print basic info on invoices."""

import argparse
import asyncio
import json

from pytekukko.examples import example_argparser, example_client, save_token


def argparser() -> argparse.ArgumentParser:
    """Return an argument parser for the example.

    This is a separate function to facilitate shtab generated completions.
    """
    return example_argparser(__doc__)


async def run_example() -> None:
    """Run the example."""
    client, token_path = example_client(argparser().parse_args())

    async with client.session:
        data = [
            {
                "invoice_number": invoice_header.invoice_number,
                "customer_number": invoice_header.customer_number,
                "name": invoice_header.name,
                "invoice_date": invoice_header.invoice_date.isoformat(),
                "due_date": invoice_header.due_date.isoformat(),
                "total": invoice_header.total,
            }
            for invoice_header in await client.get_invoice_headers()
        ]
        if not token_path:
            await client.logout()

    print(json.dumps(data))  # noqa: T201

    if token_path:
        save_token(client.token, token_path)


def main() -> None:
    """Run example in event loop."""
    asyncio.run(run_example())


if __name__ == "__main__":
    main()
