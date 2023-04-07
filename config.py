import os
import dotenv
dotenv.load_dotenv()


class config():
    def __init__(self):
        self.OpenAI = os.getenv("OPENAI_API_KEY")


config = config()
