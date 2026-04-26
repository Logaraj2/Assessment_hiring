from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1/chat/completions"
    ai_model: str = "anthropic/claude-sonnet-4"
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
