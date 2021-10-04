from enum import Enum
from typing import Dict, Optional

import os


class FinecoEndpoint(Enum):
    CHECK_CREDIT_DATE = "https://finecobank.com/conto-e-carte/bonifici/estero/checkDataAccredito"
    TRANSFER_COUNTRIES = "https://finecobank.com/conto-e-carte/bonifici/estero/ricerca-nazione-json"
    FOREIGN_TRANSFER_VALIDATION_PAGE = "https://finecobank.com/conto-e-carte/bonifici/estero/validazione"
    FOREIGN_TRANSFER_DATA_PAGE = (
        "https://finecobank.com/conto-e-carte/bonifici/estero/hub-bonifico-estero"
    )
    FOREIGN_TRANSFER_START_PAGE = "https://finecobank.com/conto-e-carte/bonifici/estero"
    LOGIN = "https://finecobank.com/portalelogin"
    PORTFOLIO_DATA = "https://finecobank.com/portafoglio/i-miei-investimenti/json/portafoglio-elenco-json"
    START_MFA_TRANSACTION = "https://finecobank.com/conto-e-carte/bonifici/estero/inizia-transazione"
    USER_PAGE = "https://finecobank.com/home/myfineco"


class FinecoClientException(Exception):
    def __init__(self, message: str):
        self.message = message


DEFAULT_FOREIGN_TRANSFER_FORM_DATA = {
    "abaBsb": "",
    "bic": "",
    "branch": "",
    "btnContinua": "continua",
    "codicePaese": None,  # internal country code
    "codiceUic": None,  # destination UIC country code
    "descrizioneBeneficiario": "",
    "divisa": "EUR",
    "divisaConto": "EUR",
    "divisaSelect": "EUR",
    "emailBeneficiario": "",
    "IbanBeneficiario": None,
    "importo": None,  # amount x,yy
    "indirizzoBeneficiario": "",
    "IntestazioneBeneficiario": None,  # beneficiary name
    "intestazioneOrdinante": None,  # fineco account name
    "lunghezzaCoordinate": None,  # IBAN length
    "nazione": None,
    "nazioneBeneficiario": None,
    "payPsd": None,  # is_pay_psd
    "serviceHome": "/conto-e-carte/bonifici/estero",
    "tipoBon": "E",
    "token": None,
    "update-amounts": None,  # amount x,yy
    "url-completo": "/conto-e-carte/bonifici/estero/ricerca-beneficiari-json",
    "url-completo-importo": "/conto-e-carte/bonifici/estero/main-currency",
    "url-nazioni": "/conto-e-carte/bonifici/estero/ricerca-nazione-json",
}
DEFAULT_FOREIGN_TRANSFER_VALIDATION_FORM_DATA = {
    "aggiungereBeneficiario": "false",
    "beneficiarioEffettivo": "",
    "btnContinua": "continua",
    "categoriaPagamento": "",
    "codicePaese": None,
    "codiceUic": None,
    "dataAccredito": None, # dd/mm/yyyy
    "Descrizione": None, # causale
    "descrizioneBeneficiario": "",
    "divisaConto": "EUR",
    "emailBeneficiario": "",
    "IbanBeneficiario": None,
    "importo": None,
    "indirizzoBeneficiario": " ",
    "IntestazioneBeneficiario": None,
    "intestazioneOrdinante": None,
    "ordinanteEffettivo": "",
    "nazione": None,
    "nazioneBeneficiario": None,
    "riferimentoBeneficiario": "",
    "riferimentoOrdinante": "",
    "riferimentoOrdinanteEffettivo": "",
    "riferimentoBeneficiarioEffettivo": "",
}

ROOT_PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
COUNTRIES_DATA_FPATH = os.path.join(ROOT_PROJECT_DIR, "countries.json")

FINECO_CLIENT_VERSION = "0.1.0"
USER_AGENT = f"fineco_client-v{FINECO_CLIENT_VERSION} github.com/ftruzzi/fineco_client/"

MAX_SEPA_DESCRIPTION_LENGTH = 140
