import os
from dotenv import load_dotenv

load_dotenv()


CHAT_LOG_DIR = os.getenv("CHAT_LOG_DIR","")