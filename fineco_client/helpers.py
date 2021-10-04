from __future__ import annotations
from typing import Any, Dict, List, Union, TYPE_CHECKING

import json
import logging

from bs4 import BeautifulSoup

import json
import locale

import requests

from .constants import COUNTRIES_DATA_FPATH, FinecoClientException

if TYPE_CHECKING:
    from .objects import FinecoPortfolioItem

logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, 'it_IT.utf8')

def str_to_float(s: str):
    return locale.atof(s)

def get_country_data(query: str) -> Dict[str, Union[int, str]]:
    countries: List[Dict[str, Union[int, str]]] = []

    with open(COUNTRIES_DATA_FPATH, "r", encoding="utf8") as f:
        countries = json.load(f)

    checkFields = lambda c: [
        c[field].upper() == query.upper()
        for field in ["descrizione", "descr_breve", "descri_eng", "descr_pay_paese"]
    ]
    selected_countries = [c for c in countries if any(checkFields(c))]
    len_selected_countries = len(selected_countries)

    if len_selected_countries == 0:
        raise FinecoClientException(f"No countries found for query {query}")
    elif len_selected_countries > 1:
        raise FinecoClientException(f"Multiple countries found for query {query}")

    return selected_countries[0]

def fetch_and_soupify(*, url: str, method: str, session: requests.Session = None, **kwargs) -> BeautifulSoup:
    if session:
        response = session.request(method=method, url=url, **kwargs)
    else:
        response = requests.request(method=method, url=url, **kwargs)

    if response.status_code == 200:
        return BeautifulSoup(response.content, "html.parser")

    logger.debug(response)
    raise FinecoClientException(f"Failed to fetch and soupify URL {url}.")

def fetch_and_parse_json(*, url: str, method: str, session: requests.Session = None, **kwargs) -> Any:
    if session:
        response = session.request(method=method, url=url, **kwargs)
    else:
        response = requests.request(method=method, url=url, **kwargs)

    if response.status_code == 200:
        return json.loads(response.text)

    logger.debug(response)
    raise FinecoClientException(f"Failed to fetch and parse JSON for URL {url}.")

def parse_portfolio_item(data: Dict) -> FinecoPortfolioItem:
    from .objects import FinecoPortfolioItem

    return FinecoPortfolioItem(
        currency=data["currencyCd"],
        description = data["descrizione"],
        isin = data["instrId"],
        quantity = int(locale.atoi(data["qty"])),
        ticker = data["titolo"],
        total_profit = locale.atof(data["profitLoss"])
    )
