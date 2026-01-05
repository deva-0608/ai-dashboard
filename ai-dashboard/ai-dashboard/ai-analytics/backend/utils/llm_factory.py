# backend/utils/llm_factory.py

from typing import Optional
from config import settings


class LLMFactory:
    """
    Central LLM factory.S
    Keeps SAME public API:
        generate_with_gemini(prompt, fallback_text)
    So agents DO NOT CHANGE.
    """

    def __init__(self):
        self._initialized = False
        self.openai_client = None
        self.groq_client = None
        self.gemini_model = None

    # --------------------------------------------------
    # Lazy initialization (as per your reference)
    # --------------------------------------------------
    def initialize_clients(self):
        if self._initialized:
            return

        self._initialized = True

        # ---------- OPENAI ----------
        if settings.ai_provider == "openai" and settings.openai_api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(
                    api_key=settings.openai_api_key
                )
                print("✅ LLM Factory: OpenAI client initialized")
            except Exception as e:
                print(f"❌ LLM Factory: OpenAI init failed: {e}")

        # ---------- GROQ ----------
        elif settings.ai_provider == "groq" and settings.groq_api_key:
            try:
                from openai import OpenAI
                self.groq_client = OpenAI(
                    api_key=settings.groq_api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                print("✅ LLM Factory: Groq client initialized")
            except Exception as e:
                print(f"❌ LLM Factory: Groq init failed: {e}")

        # ---------- GEMINI ----------
        elif settings.ai_provider == "gemini" and settings.gemini_api_key:
            try:
                import google.generativeai as genai

# Configure with your API key
                genai.configure(api_key=settings.gemini_api_key)

                # Initialize Gemini 2.5 Flash
                self.gemini_model = genai.GenerativeModel("gemini-2.5-flash")

                print("✅ LLM Factory: Gemini 2.5 Flash initialized")

                # Example usage
                # response = self.gemini_model.generate_content("Hello Gemini 2.5 Flash!")
                # print(response.text)

            except Exception as e:
                print(f"❌ LLM Factory: Gemini init failed: {e}")

    # --------------------------------------------------
    # PUBLIC API (DO NOT CHANGE NAME)
    # --------------------------------------------------
    def generate_with_gemini(self, prompt: str, fallback_text: str = "") -> str:
        """
        Universal text generation.
        Same name so agents remain untouched.
        """

        self.initialize_clients()

        try:
            # ---------- OPENAI ----------
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a data analytics planner."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.4
                )
                return response.choices[0].message.content.strip()

            # ---------- GROQ ----------
            if self.groq_client:
                response = self.groq_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": "You are a data analytics planner."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.4
                )
                return response.choices[0].message.content.strip()

            # ---------- GEMINI ----------
            if self.gemini_model:
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.4,
                        "max_output_tokens": 1024
                    }
                )
                if response and response.text:
                    return response.text.strip()

        except Exception as e:
            print("⚠️ LLM generation failed:", e)

        return fallback_text


# --------------------------------------------------
# SINGLETON + FUNCTION ALIAS
# --------------------------------------------------
_llm_factory = LLMFactory()

def generate_with_gemini(prompt: str, fallback_text: str = "") -> str:
    """
    Function wrapper so existing agents stay unchanged.
    """
    return _llm_factory.generate_with_gemini(prompt, fallback_text)
