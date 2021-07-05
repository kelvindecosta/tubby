import asyncio
from collections.abc import Callable
import click
import json
import os
import re
from typing import List, Dict, Optional

from bs4 import BeautifulSoup
import httpx
import tqdm
import tqdm.asyncio

from config import WIKI_BASE_URL
from utils import (
    clean_dict,
    gather_dict,
    load_data,
    parse_int,
    parse_tag_text,
    save_data,
)


async def get_soup(client: httpx.AsyncClient, url: str) -> BeautifulSoup:
    """Creates a soup for requested `url`

    Args:
        client (httpx.AsyncClient): HTTP client
        url (str): source URL

    Returns:
        BeautifulSoup: soup of HTML from url
    """
    req = await client.get(url)

    return BeautifulSoup(req.text, "html.parser")


async def parse_urls(client: httpx.AsyncClient, url: str) -> List[str]:
    """Gathers the list of URLs from a particular `url`

    Args:
        client (httpx.AsyncClient): HTTP client
        url (str): source URL

    Returns:
        List[str]: list of URLS
    """
    soup = await get_soup(client, url)

    return list(
        set(
            f"""{WIKI_BASE_URL}{row.find("a").get("href")}"""
            for table in soup.select("table.article-table.sortable")
            for row in table.find("tbody").find_all("tr")[1:]
        )
    )


async def parse_costs_for_furnishings_from_chubby(
    client: httpx.AsyncClient, url: str
) -> Dict[str, int]:
    """Gathers the costs for furnishings that are purchased from Chubby

    Args:
        client (httpx.AsyncClient): HTTP client
        url (str): source URL

    Returns:
        Dict[str, int]: dict of furnishing costs
    """
    soup = await get_soup(client, url)

    return {
        parse_tag_text(row.find_all("a")[1]): parse_int(
            parse_tag_text(row.find_all("td")[1])
        )
        for row in soup.find("table", {"class": "article-table"})
        .find("tbody")
        .find_all("tr")[1:]
    }


async def get_sources() -> dict:
    """Gathers intermediate data required for scraping

    Returns:
        dict: intermediate requirements
    """
    async with httpx.AsyncClient(timeout=None) as client:
        tasks = {
            f"{case.lower()}_urls": parse_urls(
                client, f"{WIKI_BASE_URL}/wiki/Housing/{case}"
            )
            for case in ["Furnishings", "Sets"]
        }

        results = await gather_dict(
            {
                **tasks,
                "costs": parse_costs_for_furnishings_from_chubby(
                    client, f"{WIKI_BASE_URL}/wiki/Chubby"
                ),
            }
        )

    return results


async def scrape_furnishing(
    client: httpx.AsyncClient, url: str, data: dict, sources: dict
):
    """Scrapes a furnishing from a `url`

    Args:
        client (httpx.AsyncClient): HTTP client
        url (str): source URL
        data (dict): database
        sources (dict): intermediate requirements
    """
    soup = await get_soup(client, url)

    name = re.sub(
        r"\/Housing$",
        "",
        parse_tag_text(soup.find("h1", {"class": "page-header__title"})),
    )

    category_heirarchy = ["categories", "subcategories", "types"]

    category, subcategory, type = [
        (
            c_map.get(c)
            if c in (c_map := data[category_heirarchy[i]]["map"])
            else [
                data[category_heirarchy[i]]["list"].append(c),
                c_map.setdefault(c, len(c_map)),
            ][1]
        )
        if c != None
        else None
        for i, c in enumerate(
            (
                list(
                    filter(
                        lambda t: len(t) > 0,
                        map(
                            lambda t: parse_tag_text(t),
                            filter(
                                lambda t: t.find("img") == None,
                                soup.find("div", {"data-source": "category"})
                                .find("div", {"class": "pi-data-value"})
                                .children,
                            ),
                        ),
                    )
                )
                + [None] * 3
            )[:3]
        )
    ]

    cost = (
        parse_int(re.search(r"\d+", cost_match.group()).group())
        if ((cost_match := re.search(r"Realm Currency.*\d+\.", soup.text)) != None)
        else (sources["costs"].get(name, None))
    )

    energy = (
        parse_int(parse_tag_text(energy_tag))
        if ((energy_tag := soup.find("td", {"data-source": "adeptal_energy"})) != None)
        else None
    )

    load = (
        parse_int(parse_tag_text(load_tag))
        if ((load_tag := soup.find("td", {"data-source": "load"})) != None)
        else None
    )

    time = (
        parse_int(
            parse_tag_text(
                time_tag.find("span", {"class": "new_genshin_recipe_header_text"})
            ).split()[0]
        )
        if (
            (time_tag := soup.find("span", {"class": "new_genshin_recipe_header_sub"}))
            != None
        )
        else None
    )

    materials = (
        {
            (
                m_map.get(m)
                if m in (m_map := data["materials"]["map"])
                else [
                    data["materials"]["list"].append(m),
                    m_map.setdefault(m, len(m_map)),
                ][1]
            ): amount
            for m, amount in {
                parse_tag_text(
                    material_tag.find("div", {"class": "card_caption"})
                ): parse_int(
                    parse_tag_text(material_tag.find("div", {"class": "card_text"}))
                )
                for material_tag in recipe_tag.findAll(
                    "div", {"class": "card_with_caption"}, recursive=False
                )
            }.items()
        }
        if (
            (recipe_tag := soup.find("div", {"class": "new_genshin_recipe_body"}))
            != None
        )
        else None
    )

    furnishing = clean_dict(
        dict(
            name=name,
            category=category,
            subcategory=subcategory,
            type=type,
            cost=cost,
            energy=energy,
            load=load,
            time=time,
            materials=materials,
        )
    )

    f_map, f_list = data["furnishings"].values()

    f_list.append(furnishing)
    f_map.setdefault(name, len(f_map))

    data["cache"][url] = True
    save_data(data)


async def scrape_set(client: httpx.AsyncClient, url: str, data: dict, sources: dict):
    """Scrapes a set from a `url`

    Args:
        client (httpx.AsyncClient): HTTP client
        url (str): source URL
        data (dict): database
        sources (dict): intermediate requirements
    """
    soup = await get_soup(client, url)

    name = re.sub(
        r"\/Housing$",
        "",
        parse_tag_text(soup.find("h1", {"class": "page-header__title"})),
    )

    category_heirarchy = ["categories", "subcategories", "types"]

    category, subcategory, type = [
        (
            c_map.get(c)
            if c in (c_map := data[category_heirarchy[i]]["map"])
            else [
                data[category_heirarchy[i]]["list"].append(c),
                c_map.setdefault(c, len(c_map)),
            ][1]
        )
        if c != None
        else None
        for i, c in enumerate(
            (
                list(
                    filter(
                        lambda t: len(t) > 0,
                        map(
                            lambda t: parse_tag_text(t),
                            filter(
                                lambda t: t.find("img") == None,
                                soup.find("div", {"data-source": "category"})
                                .find("div", {"class": "pi-data-value"})
                                .children,
                            ),
                        ),
                    )
                )
                + [None] * 3
            )[:3]
        )
    ]

    cost = (
        parse_int(re.search(r"\d+", cost_match.group()).group())
        if ((cost_match := re.search(r"Realm Currency.*\d+\.", soup.text)) != None)
        else None
    )

    mora = (
        parse_int(re.search(r"\d+", mora_match.group()).group())
        if ((mora_match := re.search(r"Mora.*\d+\.", soup.text)) != None)
        else None
    )

    energy = (
        parse_int(parse_tag_text(energy_tag))
        if ((energy_tag := soup.find("td", {"data-source": "adeptal_energy"})) != None)
        else None
    )

    load = (
        parse_int(parse_tag_text(load_tag))
        if ((load_tag := soup.find("td", {"data-source": "load"})) != None)
        else None
    )

    furnishings = (
        {
            data["furnishings"]["map"].get(f): count
            for f, count in {
                parse_tag_text(
                    furnishing_tag.find("div", {"class": "card_caption"})
                ): parse_int(
                    parse_tag_text(furnishing_tag.find("div", {"class": "card_text"}))
                )
                for furnishing_tag in recipe_tag.findAll(
                    "div", {"class": "card_with_caption"}, recursive=False
                )
            }.items()
        }
        if (
            (recipe_tag := soup.find("div", {"class": "new_genshin_recipe_body"}))
            != None
        )
        else None
    )

    companions = (
        list(
            data["furnishings"]["map"].get(
                parse_tag_text(row.find("span", {"class": "card_font"}))
            )
            for row in companions_tag[0].find("tbody").find_all("tr")[1:]
        )
        if len((companions_tag := soup.select("table.article-table.sortable"))) > 0
        else None
    )

    f_set = clean_dict(
        dict(
            name=name,
            category=category,
            subcategory=subcategory,
            type=type,
            cost=cost,
            mora=mora,
            energy=energy,
            load=load,
            furnishings=furnishings,
            companions=companions,
        )
    )

    s_map, s_list = data["sets"].values()

    s_list.append(f_set)
    s_map.setdefault(name, len(s_map))

    data["cache"][url] = True
    save_data(data)


housing_lock = asyncio.Lock()


async def scrape_urls(
    urls: List[str],
    data: dict,
    sources: dict,
    scraper: Callable[httpx.AsyncClient, str, dict, dict],
):
    """Scrapes a list of `urls`

    Args:
        urls (List[str]): subject list of URLs
        data (dict): database
        sources (dict): intermediate requirements
        scraper (Callable[httpx.AsyncClient, str, dict, dict]): individual URL scraper
    """
    async with httpx.AsyncClient(timeout=None) as client:
        async with housing_lock:
            for task in tqdm.tqdm(
                asyncio.as_completed(
                    list(scraper(client, url, data, sources) for url in urls)
                ),
                total=len(urls),
            ):
                await task


@click.command(options_metavar="[options]")
def scrape():
    """Downloads housing metadata from Genshin Impact Wiki"""

    if (data := load_data()) == None:
        print("Generating data schema...")
        data = {
            key: {"map": {}, "list": []}
            for key in [
                "categories",
                "subcategories",
                "types",
                "materials",
                "furnishings",
                "sets",
            ]
        }

        data["cache"] = {}
    else:
        print("Loaded data from local save.")

    cache = data["cache"]

    print("Refreshing sources...")
    sources = asyncio.run(get_sources())

    urls_for_furnishings = sources["furnishings_urls"]
    urls_for_sets = sources["sets_urls"]

    total_furnishings_num = len(urls_for_furnishings)
    total_sets_num = len(urls_for_sets)

    cache_filter = (
        lambda urls: urls
        if (len(cache) < 0)
        else list(filter(lambda u: u not in cache, urls))
    )

    urls_for_furnishings = cache_filter(urls_for_furnishings)
    urls_for_sets = cache_filter(urls_for_sets)

    new_furnishings_num = len(urls_for_furnishings)
    new_sets_num = len(urls_for_sets)

    if len(cache) > 0:
        print("\nLocal save has:\n")
        for key in data:
            if key != "cache":
                print(f"""  {len(data[key]["list"]):4d}  {key}""")

    if new_furnishings_num > 0:
        print(f"\nGathering {new_furnishings_num} new Furnishings...")
        asyncio.run(scrape_urls(urls_for_furnishings, data, sources, scrape_furnishing))

    if new_sets_num > 0:
        print(f"\nGathering {new_sets_num} new Sets...")
        asyncio.run(scrape_urls(urls_for_sets, data, sources, scrape_set))

    if any(map(lambda x: x > 0, (new_furnishings_num, new_sets_num))):
        print("\nHousing data updated!")
    else:
        print("\nHousing data is already up to date!")
