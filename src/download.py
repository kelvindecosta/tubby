"""This module defines functions for downloading the housing system metadata.

This metadata is gathered by scraping the Genshin Impact Wiki.
"""


import asyncio
from collections.abc import Callable
import click
import locale
import re
from typing import List, Dict


from bs4 import BeautifulSoup, Tag
import httpx
import tqdm
import tqdm.asyncio


from .file import load_metadata, save_metadata
from .reset import create_metadata_schema
from .utils import bold, clean_dict, color, gather_dict, italic


locale.setlocale(locale.LC_ALL, "en_US.UTF8")


async def fetch_soup(client: httpx.AsyncClient, url: str) -> BeautifulSoup:
    """Creates soup for HTML fetched from requested `url`

    Args:
        client (httpx.AsyncClient): HTTP client
        url (str): source URL

    Returns:
        BeautifulSoup: soup of HTML from URL
    """
    req = await client.get(url)

    return BeautifulSoup(req.text, "html.parser")


def create_wiki_url(page: str) -> str:
    """Creates canonical URL to `page` on wiki

    Args:
        page (str): subject page

    Returns:
        str: canonical URL
    """
    return f"https://genshin-impact.fandom.com{page}"


async def parse_urls(client: httpx.AsyncClient, url: str) -> List[str]:
    """Parses list of useful URLs from HTML from `url`

    Args:
        client (httpx.AsyncClient): HTTP client
        url (str): source URL

    Returns:
        List[str]: list of URLS
    """
    soup = await fetch_soup(client, url)

    return list(
        set(
            create_wiki_url(row.find("a").get("href"))
            for table in soup.select("table.article-table.sortable")
            for row in table.find("tbody").find_all("tr")[1:]
        )
    )


def get_tag_text(tag: Tag) -> str:
    """Returns stripped text in `tag`

    Args:
        tag (Tag): HTML tag

    Returns:
        str: stripped text
    """
    return tag.text.strip()


async def parse_costs_for_furnishings_from_depot(
    client: httpx.AsyncClient, url: str
) -> Dict[str, int]:
    """Parses costs for furnishings purchased from Realm Depot

    Args:
        client (httpx.AsyncClient): HTTP client
        url (str): source URL

    Returns:
        Dict[str, int]: mapping of furnishings to costs
    """
    soup = await fetch_soup(client, url)

    return {
        re.sub(r"Blueprint: ", "", get_tag_text(row.find_all("a")[1])): locale.atoi(
            get_tag_text(row.find_all("td")[1])
        )
        for table in soup.find_all("table", {"class": "article-table"})[1:]
        for row in table.find("tbody").find_all("tr")[1:-1]
    }


async def parse_costs_for_furnishings_from_chubby(
    client: httpx.AsyncClient, url: str
) -> Dict[str, int]:
    """Parses costs for furnishings purchased from Chubby

    Args:
        client (httpx.AsyncClient): HTTP client
        url (str): source URL

    Returns:
        Dict[str, int]: mapping of furnishings to costs
    """
    soup = await fetch_soup(client, url)

    return {
        get_tag_text(row.find_all("a")[1]): locale.atoi(
            get_tag_text(row.find_all("td")[1])
        )
        for row in soup.find("table", {"class": "article-table"})
        .find("tbody")
        .find_all("tr")[1:]
    }


async def fetch_sources() -> dict:
    """Fetches intermediate data required for scraping

    Returns:
        dict: mapping of source to intermediate data
    """
    async with httpx.AsyncClient(timeout=None) as client:
        tasks = {
            f"{case.lower()}_urls": parse_urls(
                client, create_wiki_url(f"/wiki/Housing/{case}")
            )
            for case in ["Furnishings", "Sets"]
        }

        tasks["chubby"] = parse_costs_for_furnishings_from_chubby(
            client, create_wiki_url("/wiki/Chubby")
        )
        tasks["depot"] = parse_costs_for_furnishings_from_depot(
            client, create_wiki_url("/wiki/Housing/Realm_Depot")
        )

        results = await gather_dict(tasks)

    return results


async def parse_furnishing(
    client: httpx.AsyncClient, url: str, metadata: dict, sources: dict
):
    """Parses furnishing from HTML from `url`

    Args:
        client (httpx.AsyncClient): HTTP client
        url (str): source URL
        metadata (dict): housing metadata
        sources (dict): intermediate data
    """
    soup = await fetch_soup(client, url)

    name = re.sub(
        r"\/Housing$",
        "",
        get_tag_text(soup.find("h1", {"class": "page-header__title"})),
    )

    category = list(
        filter(
            lambda t: len(t) > 0,
            map(
                lambda t: get_tag_text(t),
                filter(
                    lambda t: t.find("img") is None,
                    soup.find("div", {"data-source": "category"})
                    .find("div", {"class": "pi-data-value"})
                    .children,
                ),
            ),
        )
    )[0]

    cost = (
        locale.atoi(re.search(r"\d+", cost_match.group()).group())
        if ((cost_match := re.search(r"Realm Currency.*\d+\.", soup.text)) is not None)
        else (
            depot_cost
            if (depot_cost := sources["depot"].get(name)) is not None
            else sources["chubby"].get(name)
        )
    )

    materials = (
        {
            (
                m
                if m in (materials_md := metadata["materials"])
                else [materials_md.append(m), m][1]
            ): amount
            for m, amount in {
                get_tag_text(
                    material_tag.find("div", {"class": "card_caption"})
                ): locale.atoi(
                    get_tag_text(material_tag.find("div", {"class": "card_text"}))
                )
                for material_tag in recipe_tag.findAll(
                    "div", {"class": "card_with_caption"}, recursive=False
                )
            }.items()
        }
        if (
            (recipe_tag := soup.find("div", {"class": "new_genshin_recipe_body"}))
            is not None
        )
        else None
    )

    furnishing = clean_dict(
        dict(
            cost=cost,
            materials=materials,
        )
    )

    if category == "Companion":
        if name not in (companions := metadata["companions"]):
            companions.append(name)
            save_metadata(metadata)
    else:
        if (furnishings := metadata["furnishings"]).get(name) != furnishing:
            furnishings[name] = furnishing
            save_metadata(metadata)


async def parse_set(client: httpx.AsyncClient, url: str, metadata: dict, sources: dict):
    """Parses set from HTML from `url`

    Args:
        client (httpx.AsyncClient): HTTP client
        url (str): source URL
        matadata (dict): housing metadata
        sources (dict): intermediate data
    """
    soup = await fetch_soup(client, url)

    name = re.sub(
        r"\/Housing$",
        "",
        get_tag_text(soup.find("h1", {"class": "page-header__title"})),
    )

    cost = (
        locale.atoi(re.search(r"\d+", cost_match.group()).group())
        if ((cost_match := re.search(r"Realm Currency.*\d+\.", soup.text)) is not None)
        else sources["depot"].get(name)
    )

    mora = (
        locale.atoi(re.search(r"\d+", mora_match.group()).group())
        if ((mora_match := re.search(r"Mora.*\d+\.", soup.text)) is not None)
        else None
    )

    furnishings = (
        {
            get_tag_text(
                furnishing_tag.find("div", {"class": "card_caption"})
            ): locale.atoi(
                get_tag_text(furnishing_tag.find("div", {"class": "card_text"}))
            )
            for furnishing_tag in recipe_tag.findAll(
                "div", {"class": "card_with_caption"}, recursive=False
            )
        }
        if (
            (recipe_tag := soup.find("div", {"class": "new_genshin_recipe_body"}))
            is not None
        )
        else None
    )

    companions = (
        list(
            get_tag_text(row.find("span", {"class": "card_font"}))
            for row in companions_tag[0].find("tbody").find_all("tr")[1:]
        )
        if len((companions_tag := soup.select("table.article-table.sortable"))) > 0
        else None
    )

    hset = clean_dict(
        dict(
            cost=cost,
            mora=mora,
            furnishings=furnishings,
            companions=companions,
        )
    )

    if (sets := metadata["sets"]).get(name) != hset:
        sets[name] = hset
        save_metadata(metadata)


DOWNLOAD_LOCK = asyncio.Lock()


async def scrape_urls(
    urls: List[str],
    metadata: dict,
    sources: dict,
    parser: Callable[httpx.AsyncClient, str, dict, dict],
):
    """Scrapes list of `urls`

    Args:
        urls (List[str]): subject list of URLs
        metadata (dict): housing metadata
        sources (dict): intermediate data
        parser (Callable[httpx.AsyncClient, str, dict, dict]): individual URL HTML parser
    """
    async with httpx.AsyncClient(timeout=None) as client:
        async with DOWNLOAD_LOCK:
            for task in tqdm.tqdm(
                asyncio.as_completed(
                    list(parser(client, url, metadata, sources) for url in urls)
                ),
                total=len(urls),
                unit="page",
                unit_scale=False,
                unit_divisor=1,
            ):
                await task


@click.command(options_metavar="[options]")
def download():
    """Downloads housing metadata"""

    if (metadata := load_metadata()) is None:
        metadata = create_metadata_schema()

    print(italic("Refreshing sources..."))
    sources = asyncio.run(fetch_sources())

    furnishings_urls = sources["furnishings_urls"]
    sets_urls = sources["sets_urls"]

    print(f"\nGathering {bold(len(furnishings_urls))} Furnishings...")
    asyncio.run(scrape_urls(furnishings_urls, metadata, sources, parse_furnishing))

    print(f"\nGathering {bold(len(sets_urls))} Sets...")
    asyncio.run(scrape_urls(sets_urls, metadata, sources, parse_set))

    print(bold(color("\nHousing metadata updated!", "green")))
