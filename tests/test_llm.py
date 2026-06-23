import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.services.llm_service import llm_service


response = llm_service.generate(
        system_prompt="You are a helpful research assistant.",
        user_prompt="Explain AI in two sentences.",
    )

print("\nResponse:\n")
print(response)