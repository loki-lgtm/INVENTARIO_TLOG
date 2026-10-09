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

    # Origens liberadas pro CORS. Cobre os dois jeitos comuns de o Vite subir
    # em dev (localhost e 127.0.0.1) — sem isso, todo fetch do frontend falha
    # silenciosamente no navegador com erro de CORS, mesmo com o backend no ar.
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


settings = Settings()
