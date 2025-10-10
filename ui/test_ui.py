from brains.ollama_ai import OllamaAI
# from brains.openai_ai import OpenAIAI

# Switch easily between AI providers
# ai = OpenAIAI()
ai = OllamaAI(model="llama2")

print("Jarvis Brain Active...")
resp = ai.ask("Hello Jarvis, are you alive?")
print(resp)
