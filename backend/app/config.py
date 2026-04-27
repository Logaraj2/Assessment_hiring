import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.openrouter_base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.ai_model = os.getenv("AI_MODEL", "google/gemma-3-12b-it:free")
        self.cors_origins = ["*"]


settings = Settings()
