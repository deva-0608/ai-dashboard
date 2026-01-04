from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

CANDIDATE_MODELS = [
    "gemini-1.0-pro",   # most widely available
    "gemini-pro",       # legacy alias
    "gemini-1.5-pro",   # newer release with improvements
    "gemini-1.5-flash", # optimized for speed and efficiency
]


def get_llm(temperature: float = 0):
    last_error = None

    for model in CANDIDATE_MODELS:
        try:
            llm = ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature
            )
            # lightweight test
            llm.invoke("ping")
            print(f"✅ Using Gemini model: {model}")
            return llm
        except ChatGoogleGenerativeAIError as e:
            print(f"⚠️ Model unavailable: {model}")
            last_error = e

    raise RuntimeError(
        "No available Gemini models found. "
        "Enable Gemini API in Google Cloud Console."
    ) from last_error
