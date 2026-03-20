import os
import time
from groq import Groq
from dotenv import dotenv_values
from rag.models import LLMCallLog

class LLMService:
    def __init__(self):
        config = dotenv_values()  # reads .env without touching os.environ
        self.client = Groq(api_key=config.get("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def generate(self, prompt:str, user=None, session=None) -> dict:
        """
        Returns dict with: answer, prompt_tokens, compl_tokens,
                           total_tokens, latency_sec, tokens_per_sec
        Also saves a LLMCallLog row.
        """

        start = time.time()
        status = "ok"
        response_text = ''
        error_msg = ''
        usage = None

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            response_text = response.choices[0].message.content
            usage = response.usage

        except Exception as e:
            status = "error"
            error_msg = str(e)

        latency = round(time.time() - start, 3)
        tps = round(c_tokens / latency, 2) if latency > 0 and c_tokens > 0 else 0.0
        p_tokens = usage.prompt_tokens if usage else 0
        c_tokens = usage.completion_tokens if usage else 0
        t_tokens = usage.total_tokens if usage else 0

        if latency > 3 and status == 'ok':
            status = 'slow'
        # Persist Log
        LLMCallLog.objects.create(
            user=user,
            session=session,
            model=self.model,
            prompt=prompt[:2000],
            response=response_text[:4000],
            prompt_tokens=p_tokens,
            compl_tokens=c_tokens,
            total_tokens=t_tokens,
            latency_sec=latency,
            tokens_per_sec=tps,
            status=status,
            error_msg=error_msg,
        )

        return {
            "answer": response_text,
            "prompt_tokens": p_tokens,
            "compl_tokens": c_tokens,
            "total_tokens": t_tokens,
            "latency_sec": latency,
            "tokens_per_sec": tps,
            "status": status,
            "error_msg": error_msg,
        }
