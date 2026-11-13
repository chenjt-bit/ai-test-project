import os
from dotenv import load_dotenv

import pytest

load_dotenv()

# --- 这里换成你的 Coze 三件套 ---
COZE_TOKEN = os.getenv("COZE_TOKEN")
BOT_ID = os.getenv("BOT_ID")
BASE_URL = os.getenv("BASE_URL")

@pytest.fixture(scope="session")
def coze_config():
    """提供一个全局的配置读取夹具"""
    return {
        "token": COZE_TOKEN,
        "bot_id": BOT_ID,
        "base_url": BASE_URL
    }