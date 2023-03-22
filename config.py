import os
import dotenv
dotenv.load_dotenv()


class config():
    def __init__(self):
        self.Telegram_API = os.getenv("Telegram_BOT_API_Key")
        self.OpenAI = os.getenv("OPENAI_API_KEY")


config = config()
