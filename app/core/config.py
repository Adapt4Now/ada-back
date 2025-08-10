from typing import List
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseModel):
    db_user: str = "postgres"
    db_password: str = "password"
    db_host: str = "postgres_db"
    db_port: int = 5432
    db_name: str = "tasks_db"

    secret_key: str = "secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    reset_token_expire_minutes: int = 60

    api_prefix: str = "/api"
    cors_allow_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]


class DevConfig(BaseConfig):
    pass


class ProdConfig(BaseConfig):
    cors_allow_origins: List[str] = []


class TestConfig(BaseConfig):
    db_name: str = "tasks_test_db"


class Settings(BaseSettings):
    app_env: str = "dev"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def __init__(self, **data):
        super().__init__(**data)
        env = self.app_env.lower()
        if env == "prod":
            self.current_config: BaseConfig = ProdConfig()
        elif env == "test":
            self.current_config = TestConfig()
        else:
            self.current_config = DevConfig()


settings = Settings()
