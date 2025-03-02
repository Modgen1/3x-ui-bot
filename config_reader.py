from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    admin_id: SecretStr
    panel_host: SecretStr
    panel_port: SecretStr
    panel_uri_path: SecretStr
    panel_login: SecretStr
    panel_password: SecretStr
    server_url: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()
