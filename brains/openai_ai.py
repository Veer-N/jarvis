import os
from dotenv import load_dotenv
from openai import OpenAI
from brains.base_ai import BaseAI

class OpenAIAI(BaseAI):
    def __init__(self):
        load_dotenv("credentials/.env")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def ask(self, prompt: str) -> str:
        try:
            resp = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"OpenAI error: {str(e)}"
