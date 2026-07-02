class LLMService:
    """
    Centralized Ollama service used by all agents.
    """

    def __init__(self):
        from backend.config.settings import settings

        try:
            from ollama import Client
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "The 'ollama' package is required. Install project dependencies with "
                "`python -m pip install -r requirements.txt` from your active virtual environment."
            ) from exc

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


class LazyLLMService:
    def __init__(self):
        self._service: LLMService | None = None

    def _get_service(self) -> LLMService:
        if self._service is None:
            self._service = LLMService()
        return self._service

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
    ) -> str:
        return self._get_service().generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )


llm_service = LazyLLMService()
