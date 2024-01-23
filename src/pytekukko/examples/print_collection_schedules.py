#!/usr/bin/env python3

"""Print collection schedules."""

import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone

import icalendar

import pytekukko
from pytekukko.examples import example_argparser, example_client


async def run_example() -> None:
    """Run the example."""
    argparser = example_argparser(__doc__)
    argparser.add_argument(
        "-i", "--icalendar", action="store_true", help="output iCalendar"
    )
    args = argparser.parse_args()

    client, cookie_jar, cookie_jar_path = example_client(args)

    async with client.session:
        data = [
            (service, await client.get_collection_schedule(service))
            for service in await client.get_services()
            if service.next_collection
        ]
        if not cookie_jar_path:
            await client.logout()

    if args.icalendar:
        now = datetime.now(tz=timezone.utc)
        cal = icalendar.Calendar()
        cal.add("PRODID", f"pytekukko/{pytekukko.__version__}")
        cal.add("VERSION", "2.0")
        cal.add("NAME", "Jätekukko collections")
        cal.add("X-WR-CALNAME", "Jätekukko collections")
        cal.add("URL", "https://tilasto.jatekukko.fi/indexservice2.jsp")
        cal.add("X-WR-TIMEZONE", "Europe/Helsinki")
        cal.add("METHOD", "PUBLISH")
        for service, schedule in data:
            for date in schedule:
                event = icalendar.Event()
                event.add("UID", f"pytekukko-{service.pos}-{date}@scop.github.io")
                event.add("SUMMARY", service.name)
                event.add("DTSTAMP", now)
                event.add("DTSTART", date)
                event.add("DTEND", date + timedelta(days=1))
                event.add("URL", "https://tilasto.jatekukko.fi/indexservice2.jsp")
                cal.add_component(event)
        sys.stdout.buffer.write(cal.to_ical())
    else:
        print(  # noqa: T201 # intentional
            json.dumps(
                [
                    {
                        "name": service.name,
                        "collection_schedule": [date.isoformat() for date in schedule],
                    }
                    for service, schedule in data
                ]
            )
        )

    if cookie_jar_path:
        cookie_jar.save(cookie_jar_path)


def main() -> None:
    """Run example in event loop."""
    asyncio.run(run_example())


if __name__ == "__main__":
    main()
