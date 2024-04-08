import json
from pathlib import Path
from dotenv import load_dotenv

from pydantic_settings import BaseSettings

from logger import logger

env_file = Path().resolve().parent / "env" / ".env"


class Config(BaseSettings):
    parse_timeout: int = 1 * 60  # 1 min
    request_attempts: int = 3
    upwork_query: str = "python"
    target_language: str = "english"

    chat_ids_file: Path = Path().resolve().parent / "data" / "chat_ids.json"
    jobs_file: Path = Path().resolve().parent / "data" / "jobs.pickle"
    chat_ids: list[int | str] = []

    upwork_bot_token: str
    openai_key: str
    upwork_token: str
    upwork_user_id: str
    upwork_org_id: str

    def __init__(self, *args, **kwargs):
        load_dotenv(env_file)
        super().__init__(*args, **kwargs)
        self.load_chat_ids()

    def load_chat_ids(self):
        logger.info("Loading chat_ids from file")
        try:
            with open(self.chat_ids_file, "r") as f:
                self.chat_ids = json.load(f)
        except:
            logger.warning("Failed to load chat_ids to file")

    def add_user_id(self, user_id):
        self.chat_ids.append(user_id)
        self.chat_ids = list(set(self.chat_ids))
        self.dump_chat_ids()

    def dump_chat_ids(self):
        logger.info("Dumping chat_ids from file")
        try:
            with open(self.chat_ids_file, "w") as f:
                json.dump(self.chat_ids, f)
        except:
            logger.warning("Failed to dump chat_ids to file")


cfg = Config()
