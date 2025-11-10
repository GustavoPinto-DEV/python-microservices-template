"""Config - Variables de entorno"""
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

APP_ENV = {
    "timestamp": datetime.now().isoformat(),
    "environment": os.getenv("ENVIRONMENT", "dev"),
}

def get_env(key: str, default=None):
    return os.getenv(key, default)
