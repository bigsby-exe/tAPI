from pydantic_settings import BaseSettings
from pydantic import model_validator
from urllib.parse import quote_plus
from typing import Self


class Settings(BaseSettings):
    API_KEY: str
    DATABASE_URL: str = ""
    
    # Individual database components (for Docker Compose)
    POSTGRES_HOST: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_PORT: int = 5432

    class Config:
        env_file = ".env"
    
    @model_validator(mode='after')
    def construct_database_url(self) -> Self:
        # If DATABASE_URL is not set, construct it from individual components
        if not self.DATABASE_URL and all([
            self.POSTGRES_HOST,
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_DB
        ]):
            # URL-encode the password and user to handle special characters
            encoded_password = quote_plus(self.POSTGRES_PASSWORD)
            encoded_user = quote_plus(self.POSTGRES_USER)
            self.DATABASE_URL = (
                f"postgresql://{encoded_user}:{encoded_password}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        
        # Validate that DATABASE_URL is set
        if not self.DATABASE_URL:
            raise ValueError(
                "Either DATABASE_URL must be set, or all of POSTGRES_HOST, "
                "POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB must be set"
            )
        
        return self


settings = Settings()
