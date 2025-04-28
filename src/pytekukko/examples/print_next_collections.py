#!/usr/bin/env python3

"""Print next collection dates."""

import argparse
import asyncio
import json

from pytekukko.examples import example_argparser, example_client


def argparser() -> argparse.ArgumentParser:
    """Return an argument parser for the example.

    This is a separate function to facilitate shtab generated completions.
    """
    return example_argparser(__doc__)


async def run_example() -> None:
    """Run the example."""
    client, cookie_jar, cookie_jar_path = example_client(argparser().parse_args())

    async with client.session:
        data = [
            {
                "name": service.name,
                "collection_date": service.next_collection.isoformat(),
            }
            for service in await client.get_services()
            if service.next_collection
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
