import os
from dotenv import load_dotenv

load_dotenv()


CHAT_LOG_DIR = os.getenv("CHAT_LOG_DIR","")

SMTP_CONFIG = {
    "host":  os.getenv("SMTP_HOST",""),
    "port": os.getenv("SMTP_PORT",""),
    "sender_email":  os.getenv("SMTP_SENDER",""),
    "password":  os.getenv("app_password","")
}
