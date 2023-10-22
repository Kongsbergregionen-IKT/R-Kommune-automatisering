from typing import Optional, Literal, TypedDict
import requests

API_TIMEOUT = 10


class FiksRegister:
    """Fiks Register. Documentation: https://developers.fiks.ks.no/tjenester/register/"""

    def __init__(
        self,
        env: Literal["test", "prod"] = "test",
        role_id: Optional[str] = None,
        integration_id: Optional[str] = None,
        integration_password: Optional[str] = None,
    ) -> None:
        """Init"""
        self.env = None
        self.env_url = None
        self.role_id = None
        self.integration_id = None
        self.integration_password = None
        self.configure_integration_client(
            env, role_id, integration_id, integration_password
        )

    def configure_integration_client(
        self,
        env: Literal["test", "prod"],
        role_id: str,
        integration_id: str,
        integration_password: str,
    ) -> None:
        """Load integration client"""
        self.env = env
        if env == "test":
            self.env_url = "https://api.fiks.test.ks.no"
        elif env == "prod":
            self.env_url = "https://api.fiks.ks.no"
        self.role_id = role_id
        self.integration_id = integration_id
        self.integration_password = integration_password

    def _post_request(self, token: str, url_endpoint: str, json_body: dict) -> dict:
        """Post request and return response from API"""
        request_url = f"{self.env_url}{url_endpoint}"
        auth_headers = {
            "Authorization": "Bearer " + token,
            "IntegrasjonId": self.integration_id,
            "IntegrasjonPassord": self.integration_password,
        }
        response = requests.post(
            url=request_url,
            headers=auth_headers,
            json=json_body,
            timeout=API_TIMEOUT,
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            print(error.response.text)
            raise error
        response_json = response.json()
        return response_json


class SummertSkattegrunnlag(FiksRegister):
    """Fiks register summert skattegrunnlag service v2. Documentation:
    https://editor.swagger.io/?url=https://developers.fiks.ks.no/api/register-summert-skattegrunnlag-api-v2.json
    """

    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()

    class Applicant(TypedDict):
        "Class for applicants (soekere) for use in Fiks register summert skattegrunnlag service"
        personidentifikator: str
        personType: Literal[
            "SOEKER",
            "EKTEFELLE",
            "PARTNER",
            "SAMBOER",
            "BARN",
            "SOESKEN",
            "MOR",
            "FAR",
            "MEDMOR",
            "ANNET",
        ]

    def get_summert_skattegrunnlag(
        self,
        income_year: str,
        calculation_type: Literal[
            "BARNEHAGE_SFO", "PRAKTISK_BISTAND", "LANGTIDSOPPHOLD_INSTITUSJON"
        ],
        applicants: list[Applicant],
        access_token: str,
    ) -> dict:
        """Get summert skattegrunnlag for applicant(s).
        API-documentation:
        https://editor.swagger.io/?url=https://developers.fiks.ks.no/api/register-summert-skattegrunnlag-api-v2.json
        """
        endpoint = f"/register/api/v2/ks/{self.role_id}/summertskattegrunnlag"
        body = self._summert_skattegrunnlag_create_request_body(
            income_year, calculation_type, applicants
        )
        response = self._post_request(
            token=access_token, url_endpoint=endpoint, json_body=body
        )
        return response

    def _summert_skattegrunnlag_create_request_body(
        self,
        income_year: str,
        calculation_type: Literal[
            "BARNEHAGE_SFO", "PRAKTISK_BISTAND", "LANGTIDSOPPHOLD_INSTITUSJON"
        ],
        applicants: list[Applicant],
    ) -> dict:
        """Create a request body for the summert skattegrunnlag API"""
        body = {
            "soekere": applicants,
            "inntektsaar": income_year,
            "beregningstype": calculation_type,
        }
        return body
