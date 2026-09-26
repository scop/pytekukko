#!/usr/bin/env python3

# Copyright 2021 Ville Skyttä

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
        infos = await client.emptying_infos()
        info_contracts = await asyncio.gather(*(client.contracts(i.id) for i in infos))
        data = [
            {"name": contract.name, "next_emptying": contract.next_emptying.isoformat()}
            for info_contract in info_contracts
            for contract in info_contract
            if contract.next_emptying
        ]
        await client.logout()

    print(json.dumps(data))  # noqa: T201 if contract.all_emptyings

    if cookie_jar_path:
        cookie_jar.save(cookie_jar_path)


def main() -> None:
    """Run example in event loop."""
    asyncio.run(run_example())


if __name__ == "__main__":
    main()
