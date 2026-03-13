import os
from groq import Groq
from dotenv import load_dotenv



class LLMService:
    def __init__(self):
        load_dotenv()
        self.client = Groq(os.getenv("GROQ_API_KEY"))
        self.model = "llama3-70b-8192"

    def generate(self, prompt:str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        return response.choices[0].message.content
