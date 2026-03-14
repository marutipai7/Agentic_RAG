import os
from groq import Groq
from dotenv import dotenv_values


class LLMService:
    def __init__(self):
        config = dotenv_values()  # reads .env without touching os.environ
        self.client = Groq(api_key=config.get("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def generate(self, prompt:str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        return response.choices[0].message.content
