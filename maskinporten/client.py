from typing import Optional, Union, Literal
from datetime import datetime, timezone, timedelta
import jwt
import requests
from cryptography.hazmat.primitives import serialization

API_TIMEOUT = 30


class Maskinporten:
    """Class for konfigurering av Maskinporten-klient og henting av access_token (tilgangsnøkkel) fra Maskinporten"""

    def __init__(
        self,
        env: Literal["test", "prod"] = "test",
        client_id: Optional[str] = None,
        scope: Optional[str] = None,
        private_key_path: Optional[str] = None,
        key_id: Optional[str] = None,
        consumer_org: Optional[str] = None,
    ) -> None:
        """Init og direktekonfigurasjon av Maskinporten-klient"""
        self.env = None
        self.client_id = None
        self.scope = None
        self.private_key_path = None
        self.key_id = None
        self.consumer_org = None
        self.env_url = None
        self.configure_maskinporten_client(
            client_id=client_id,
            scope=scope,
            private_key_path=private_key_path,
            key_id=key_id,
            env=env,
            consumer_org=consumer_org,
        )

    def configure_maskinporten_client(
        self,
        client_id: str,
        scope: str,
        private_key_path: str,
        key_id: str,
        env: str = Literal["test", "prod"],
        consumer_org: Optional[str] = None,
    ) -> Union[str, None]:
        """Konfigurerer Maskinporten-klient"""
        if env == "prod":
            self.env_url = ""
        elif env == "test":
            self.env_url = "test."
        self.env = env
        self.client_id = client_id
        self.scope = scope
        self.private_key_path = private_key_path
        self.key_id = key_id
        self.consumer_org = consumer_org

    def get_access_token(self) -> str:
        """Returnerer access token fra Maskinporten"""
        response = self._get_response()
        return response["access_token"]

    def _get_response(self) -> dict:
        """Returnerer fullstendig respons fra Maskinporten"""
        jwt_grant = self._generate_jwt_grant(pem=self.private_key_path, kid=self.key_id)
        endpoint = f"https://{self.env_url}maskinporten.no/token"
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        body = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": jwt_grant,
        }
        response = requests.post(
            url=endpoint, headers=header, params=body, timeout=API_TIMEOUT
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            print(error.response.text)
            raise error
        response_json = response.json()
        return response_json

    def _generate_jwt_grant(self, pem: str, kid: str) -> str:
        """Genererer JWT grant fra private key"""
        private_key = self._read_pem_private_key(pem_path=pem)
        key = serialization.load_pem_private_key(private_key.encode(), password=None)
        jwt_grant = jwt.encode(
            payload={
                "aud": f"https://{self.env_url}maskinporten.no/",
                "iss": self.client_id,
                "scope": self.scope,
                "iat": datetime.now(tz=timezone.utc),
                "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=120),
                "consumer_org": self.consumer_org,
            },
            key=key,
            headers={"alg": "RS256", "kid": kid},
        )
        return jwt_grant

    def _read_pem_private_key(self, pem_path: str) -> str:
        "Leser RSA Private Key fra oppgitt PEM-fil"
        with open(pem_path, "r", encoding="utf-8") as private_key:
            return private_key.read()
