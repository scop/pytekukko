#!/usr/bin/env python3

"""Print next collection dates."""

import asyncio
import json

from pytekukko.examples import example_argparser, example_client


async def run_example() -> None:
    """Run the example."""
    client, cookie_jar, cookie_jar_path = example_client(
        example_argparser(__doc__).parse_args(),
    )

    data = []
    async with client.session:
        services = await client.get_services()
        for service in (x for x in services if x.next_collection):
            data.append(
                {
                    "name": service.name,
                    "collection_date": service.next_collection.isoformat(),  # type: ignore[union-attr]
                },
            )
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
