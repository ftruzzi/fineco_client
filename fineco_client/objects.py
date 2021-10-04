import logging

from .constants import MAX_SEPA_DESCRIPTION_LENGTH, FinecoClientException
from .helpers import get_country_data

logger = logging.getLogger(__name__)


class FinecoBankTransfer:
    def __init__(
        self,
        *,
        amount: float,
        description: str,
        recipient_country: str,
        recipient_iban: str,
        recipient_name: str,
    ) -> None:
        self.amount = amount
        # self.currency = currency
        self.description = description
        self.recipient_country = recipient_country
        self.recipient_iban = recipient_iban
        self.recipient_name = recipient_name

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        rounded_amount = round(value, 2)
        if rounded_amount != value:
            logger.warning(
                f"Transfer amount value rounded from {value} to {rounded_amount}"
            )
        self._amount = rounded_amount

    @property
    def recipient_country(self):
        return self._recipient_country

    @recipient_country.setter
    def recipient_country(self, value):
        if country_data := get_country_data(value):
            self._country_data = country_data
            self._recipient_country = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        value = value.strip()
        if len(value) > MAX_SEPA_DESCRIPTION_LENGTH:
            raise FinecoClientException(
                f"Transfer description is too long ({len(value)}/{MAX_SEPA_DESCRIPTION_LENGTH} chars)"
            )
        self._description = value


class FinecoPortfolioItem:
    def __init__(
        self,
        *,
        currency: str,
        description: str,
        isin: str,
        quantity: int,
        ticker: str,
        total_profit: float,
    ):
        self.currency = currency
        self.description = description
        self.isin = isin
        self.quantity = quantity
        self.ticker = ticker
        self.total_profit = total_profit

    def __repr__(self):
        values = { k: v for k, v in self.__dict__.items() if v is not None }
        return f"<FinecoPortfolioItem: {values}>"
