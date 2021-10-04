from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Tuple, TYPE_CHECKING

import json
import logging
import os

from bs4 import BeautifulSoup
from requests.sessions import Session

from .constants import (
    FinecoEndpoint,
    FinecoClientException,
    COUNTRIES_DATA_FPATH,
    DEFAULT_FOREIGN_TRANSFER_FORM_DATA,
    USER_AGENT,
)
from .helpers import fetch_and_parse_json, fetch_and_soupify, parse_portfolio_item
from .objects import FinecoBankTransfer

if TYPE_CHECKING:
    from .objects import FinecoPortfolioItem

logger = logging.getLogger(__name__)


class FinecoClient:
    _account_holder: str
    _username: str
    _password: str
    _session: Session

    def __init__(
        self,
        *,
        username: str = str(os.getenv("FINECO_USER")),
        password: str = str(os.getenv("FINECO_PASS")),
    ) -> None:
        if not username or not password:
            logger.error(
                "Missing username and/or password. Either pass them to the FinecoClient constructor or set FINECO_USER and FINECO_PASS environment variables."
            )

        self._username = username
        self._password = password
        self._session = Session()
        self._session.headers.update({"User-Agent": USER_AGENT})
        self._login()

    def _login(self):
        data = {"LOGIN": self._username, "PASSWD": self._password}
        response = self._session.request(
            method="POST", url=FinecoEndpoint.LOGIN.value, data=data
        )
        if (
            response.status_code != 200
            or response.url != FinecoEndpoint.USER_PAGE.value
        ):
            logger.debug(response.text)
            raise FinecoClientException(
                f"Login failed: status_code {response.status_code}, url: {response.url}"
            )

        soup = BeautifulSoup(response.text, "html.parser")
        self._account_holder = soup.select_one(".intestazione").text.strip()

    def _get_first_available_transfer_date(self, recipient_iban: str):
        params = {
            "datautente": datetime.now().strftime(r"%Y%m%d"),
            "ibanbeneficiario": recipient_iban,
        }
        response = self._session.request(
            method="GET", url=FinecoEndpoint.CHECK_CREDIT_DATE.value, params=params
        )
        response.raise_for_status()

        data = json.loads(response.text)["data"]
        first_available_date = data["primaDataUtileFormatted"]
        logger.info(f"Selecting {first_available_date} as first available date.")
        return first_available_date

    def _get_new_transfer_token(self):
        soup = fetch_and_soupify(
            session=self._session,
            method="GET",
            url=FinecoEndpoint.FOREIGN_TRANSFER_START_PAGE.value,
        )
        token = soup.select_one("#token")
        return token.attrs["value"] + "1"

    def _create_transfer_form_data(
        self, transfer: FinecoBankTransfer
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        amount = str(transfer.amount).replace(".", ",")
        data_first_step = {
            "codicePaese": transfer._country_data["cod_paese"],
            "codiceUic": transfer._country_data["cod_uic"],
            "IbanBeneficiario": transfer.recipient_iban,
            "importo": amount,
            "IntestazioneBeneficiario": transfer.recipient_name,
            "intestazioneOrdinante": self._account_holder,
            "lunghezzaCoordinate": len(transfer.recipient_iban),
            "nazione": transfer._country_data["cod_iso"],
            "nazioneBeneficiario": transfer._country_data["descrizione"],
            "payPsd": transfer._country_data["is_pay_psd"],
            "token": self._get_new_transfer_token(),
            "update-amounts": amount,
        }

        data_second_step = {
            "codicePaese": transfer._country_data["cod_paese"],
            "codiceUic": transfer._country_data["cod_uic"],
            "dataAccredito": self._get_first_available_transfer_date(
                transfer.recipient_iban
            ),
            "descrizione": transfer.description,
            "nazioneBeneficiario": transfer._country_data["descrizione"],
            "IbanBeneficiario": transfer.recipient_iban,
            "importo": amount,
            "IntestazioneBeneficiario": transfer.recipient_name,
            "intestazioneOrdinante": self._account_holder,
            "nazione": transfer._country_data["cod_iso"],
            "nazioneBeneficiario": transfer._country_data["descrizione"],
        }

        data_first_step = {**DEFAULT_FOREIGN_TRANSFER_FORM_DATA, **data_first_step}
        data_second_step = {**DEFAULT_FOREIGN_TRANSFER_FORM_DATA, **data_second_step}

        return data_first_step, data_second_step

    def send_transfer(self, transfer: FinecoBankTransfer):
        data_first_step, data_second_step = self._create_transfer_form_data(transfer)

        response = self._session.request(
            method="POST",
            url=FinecoEndpoint.FOREIGN_TRANSFER_DATA_PAGE.value,
            data=data_first_step,
        )
        response.raise_for_status()

        soup = fetch_and_soupify(
            session=self._session,
            method="POST",
            url=FinecoEndpoint.FOREIGN_TRANSFER_VALIDATION_PAGE.value,
            data=data_second_step,
        )
        mfa_token = soup.select_one(".token-bonifici").text.strip() # type: ignore

        response = self._session.request(
            method="POST",
            url=FinecoEndpoint.START_MFA_TRANSACTION.value,
            data={"token": mfa_token},
        )
        response.raise_for_status()

    def get_portfolio(self) -> List[FinecoPortfolioItem]:
        data: List[List[Dict[str, Any]]] = fetch_and_parse_json(
            method="GET", url=FinecoEndpoint.PORTFOLIO_DATA.value, session=self._session
        )
        return [parse_portfolio_item(i) for i in data[0]]

    def update_countries_file(self):
        from string import ascii_lowercase

        # A fake transfer is needed to set proper cookies
        fake_transfer = FinecoBankTransfer(
            amount=0.01,
            description="Fake transfer",
            recipient_country="BELGIUM",
            recipient_iban="BE00000000000000",
            recipient_name="Fake person",
        )
        data_first_step, _ = self._create_transfer_form_data(fake_transfer)
        response = self._session.request(
            method="POST",
            url=FinecoEndpoint.FOREIGN_TRANSFER_DATA_PAGE.value,
            data=data_first_step,
        )
        response.raise_for_status()

        countries = []
        for letter in ascii_lowercase:
            response = self._session.request(
                method="POST",
                url=FinecoEndpoint.TRANSFER_COUNTRIES.value,
                data={"term": letter + " "},
                allow_redirects=False,
            )
            response.raise_for_status()
            data: List[Dict] = json.loads(response.text)
            for country in data:
                if country not in countries:
                    countries.append(country)

        with open(COUNTRIES_DATA_FPATH, "w", encoding="utf8") as f:
            json.dump(
                sorted(countries, key=lambda c: c["descrizione"]), f, ensure_ascii=False
            )
