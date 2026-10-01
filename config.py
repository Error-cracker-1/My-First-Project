import os
from dataclasses import dataclass

from dotenv import load_dotenv


DEFAULT_MODEL = "gemini-3.5-flash-lite"
DEFAULT_MAX_OUTPUT_TOKENS = 2048

SUPPORTED_MODELS = {
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
}


@dataclass(frozen=True)
class ChatbotConfig:
    api_key: str
    model: str = DEFAULT_MODEL
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS

    @classmethod
    def from_env(cls) -> "ChatbotConfig":
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. Add it to your .env file."
            )

        model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip()
        if model not in SUPPORTED_MODELS:
            print(
                f"Unknown GEMINI_MODEL '{model}'. "
                f"Using {DEFAULT_MODEL}."
            )
            model = DEFAULT_MODEL

        raw_tokens = os.getenv(
            "GEMINI_MAX_OUTPUT_TOKENS",
            str(DEFAULT_MAX_OUTPUT_TOKENS),
        ).strip()

        try:
            max_output_tokens = int(raw_tokens)
        except ValueError as error:
            raise RuntimeError(
                "GEMINI_MAX_OUTPUT_TOKENS must be a positive integer."
            ) from error

        if max_output_tokens <= 0:
            raise RuntimeError(
                "GEMINI_MAX_OUTPUT_TOKENS must be a positive integer."
            )

        return cls(
            api_key=api_key,
            model=model,
            max_output_tokens=max_output_tokens,
        )
