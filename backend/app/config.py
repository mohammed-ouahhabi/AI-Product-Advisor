import os
from dataclasses import dataclass


@dataclass
class Settings:
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///ai_product_advisor.db')
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'change-me-in-production')

    HF_MODEL_NAME: str = os.getenv(
        'HF_MODEL_NAME',
        'distilbert-base-uncased-finetuned-sst-2-english',
    )
    HF_TASK: str = os.getenv('HF_TASK', 'sentiment-analysis')

    HF_TEXT2TEXT_MODEL: str = os.getenv('HF_TEXT2TEXT_MODEL', 'google/flan-t5-base')


settings = Settings()
