# brains/ollama_ai.py
import requests
import json

class OllamaAI:
    def __init__(self, model="llama2"):   # default back to llama2
        self.model = model
        self.base_url = "http://localhost:11434/api/generate"

    def ask(self, prompt: str) -> str:
        payload = {"model": self.model, "prompt": prompt}
        resp = requests.post(self.base_url, json=payload, stream=True)

        answer = ""
        for line in resp.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    answer += data.get("response", "")
                except Exception:
                    continue
        return answer.strip()
