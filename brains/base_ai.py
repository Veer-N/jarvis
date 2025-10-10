class BaseAI:
    def ask(self, prompt: str) -> str:
        """Send a prompt to the AI and return the response"""
        raise NotImplementedError("This method must be overridden by subclasses")
