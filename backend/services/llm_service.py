from ollama import Client

from backend.config.settings import settings


class LLMService:
    """
    Centralized Ollama service used by all agents.
    """

    def __init__(self):
        self.client = Client(host=settings.OLLAMA_BASE_URL)
        self.model = settings.OLLAMA_MODEL

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
    ) -> str:
        """
        Generate a response from the local Ollama model.
        """

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            options={
                "temperature": temperature,
            },
        )

        return response["message"]["content"]


llm_service = LLMService()