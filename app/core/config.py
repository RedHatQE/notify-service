import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, validator, RedisDsn


class Settings(BaseSettings):
    DOMAIN: str
    PORT: str
    # Default deploy target is openshift
    TARGET: str = "openshift"
    # Default ssl is enabled with openshift route tls termination set as edge
    SSL_ENABLED: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # SERVER_NAME: str
    # SERVER_HOST: AnyHttpUrl
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str
    SENTRY_DSN: Optional[HttpUrl] = None

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    os.getcwdb()
    EMAIL_TEMPLATES_DIR: str = os.path.join(os.getcwdb().decode(), "app/templates/build")
    EMAILS_ENABLED: bool = True

    TEMPLATE_MOUNT_DIR: Optional[str] = None

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore

    REDIS_URI: RedisDsn
    REDIS_PASSWORD: Optional[str] = None

    GCHAT_WEBHOOK_URL: Optional[AnyHttpUrl] = None
    SLACK_WEBHOOK_URL: Optional[AnyHttpUrl] = None

    CERT_PATH: Optional[str] = None
    KEY_FILE_NAME: Optional[str] = None
    CERT_FILE_NAME: Optional[str] = None
    CA_CERTS_NAME: Optional[str] = None

    MSG_BUS_HOST_1: Optional[str] = None
    MSG_BUS_PORT_1: Optional[int] = None
    MSG_BUS_HOST_2: Optional[str] = None
    MSG_BUS_PORT_2: Optional[int] = None
    MSG_DEFAULT_TOPIC: Optional[str] = None

    IRC_SERVER: Optional[str] = None
    IRC_SERVER_PORT: Optional[int] = 6667
    IRC_SSL: Optional[bool] = False
    IRC_NICKNAME: Optional[str] = "notify-service-noreply"
    # Default channel name start with '#' or username
    IRC_TARGET: Optional[str] = None
    IRC_PASSWORD: Optional[str] = None


    class Config:
        case_sensitive = True


settings = Settings()
