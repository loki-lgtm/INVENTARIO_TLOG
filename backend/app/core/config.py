from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./app.db"
    secret_key: str = "changeme"

    glpi_api_url: str = ""
    glpi_app_token: str = ""
    glpi_user_token: str = ""

    docusign_api_url: str = ""
    docusign_account_id: str = ""
    docusign_client_id: str = ""
    docusign_client_secret: str = ""


settings = Settings()
