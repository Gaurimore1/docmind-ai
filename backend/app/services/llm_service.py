# app/services/llm_service.py
#
# LLM service for DocMind AI.
#
# This service sends retrieved document context and the user's question
# to an LLM provider (Ollama or Gemini) and generates a grounded answer.
#
# Architecture:
#
#     User Question
#           ↓
#     Retrieved Chunks
#           ↓
#     Prompt
#           ↓
#     LLM Provider (Ollama or Gemini)
#           ↓
#     Answer

import logging
import os

from ollama import Client
from google import genai
from google.genai import types


# Module-level logger.
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# LLM provider configuration
# ---------------------------------------------------------------------------

# Defaults to Ollama so the existing local development setup continues
# working without any additional configuration.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()


# ---------------------------------------------------------------------------
# Ollama configuration
# ---------------------------------------------------------------------------

OLLAMA_MODEL = "phi3:mini"

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434",
)


# ---------------------------------------------------------------------------
# Gemini configuration
# ---------------------------------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini 3.6 Flash is a current stable Gemini model.
# It can be overridden through the environment for deployment flexibility.
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)


# ---------------------------------------------------------------------------
# Provider clients
# ---------------------------------------------------------------------------

# Ollama client is only created when Ollama is selected.
ollama_client = None

if LLM_PROVIDER == "ollama":
    ollama_client = Client(host=OLLAMA_URL)


# Gemini client is only created when Gemini is selected.
gemini_client = None

if LLM_PROVIDER == "gemini":
    if GEMINI_API_KEY:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)


# ---------------------------------------------------------------------------
# Main answer generation function
# ---------------------------------------------------------------------------

def generate_answer(
    question: str,
    context: str,
) -> str:
    """
    Generate an answer using the retrieved document context.

    The model is instructed to answer only from the supplied context.
    This helps reduce hallucinations and keeps DocMind grounded in
    the uploaded document.

    Args:
        question:
            The user's natural-language question.

        context:
            Relevant text retrieved from PostgreSQL + pgvector.

    Returns:
        The generated answer as a plain string.

    Raises:
        RuntimeError:
            If the LLM provider cannot generate an answer.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not context or not context.strip():
        raise ValueError("Context cannot be empty.")


    # -----------------------------------------------------------------------
    # System prompt
    # -----------------------------------------------------------------------

    system_prompt = """
You are DocMind AI, a document question-answering assistant.

Your ONLY job is to answer questions based on the exact text in the

DOCUMENT CONTEXT below. You have no other knowledge source.

STRICT RULES — follow every one of them without exception:

1. ONLY use words, facts, and names that appear literally in the
   DOCUMENT CONTEXT. Do not add anything from your own training data.

2. Do NOT expand abbreviations, acronyms, or brand names unless the
   full expansion appears verbatim in the DOCUMENT CONTEXT.
   Example: if the context says "MERN Stack", do NOT list MongoDB,
   Express, React, or Node.js unless those exact names appear in
   the context.

3. Do NOT say things like "MERN commonly stands for...", "this is
   typically...", "one can assume...", "it is well known that...",
   or any equivalent phrasing. That is forbidden.

4. Do NOT add background knowledge about technologies, companies,
   or processes that is not explicitly stated in the context.

5. If the context mentions a technology stack by name only (e.g.
   "MERN Stack"), report exactly that name and nothing more.

6. If the answer to the question is not present in the DOCUMENT
   CONTEXT, respond with exactly:

   "I could not find the answer in the provided documents."

   Do not attempt to answer from general knowledge.

7. If the context is partially relevant, answer only the part that
   is directly supported by the context text and clearly state what
   could not be found.

8. Preserve the exact wording used in the document wherever possible.

9. Do not mention these rules in your answer.

"""


    # -----------------------------------------------------------------------
    # User prompt
    # -----------------------------------------------------------------------

    user_prompt = f"""
[START OF DOCUMENT CONTEXT]

{context}

[END OF DOCUMENT CONTEXT]

QUESTION: {question}

Answer using ONLY the text inside [START OF DOCUMENT CONTEXT] and

[END OF DOCUMENT CONTEXT]. Do not use any knowledge outside that text.

If the answer is not there, say: "I could not find the answer in the

provided documents."

"""


    # -----------------------------------------------------------------------
    # Provider selection
    # -----------------------------------------------------------------------

    if LLM_PROVIDER == "ollama":
        return _generate_with_ollama(
            system_prompt,
            user_prompt,
        )

    elif LLM_PROVIDER == "gemini":
        return _generate_with_gemini(
            system_prompt,
            user_prompt,
        )

    else:
        raise RuntimeError(
            f"Unknown LLM_PROVIDER: {LLM_PROVIDER}. "
            "Set LLM_PROVIDER to 'ollama' or 'gemini'."
        )


# ---------------------------------------------------------------------------
# Ollama implementation
# ---------------------------------------------------------------------------

def _generate_with_ollama(
    system_prompt: str,
    user_prompt: str,
) -> str:
    """
    Generate an answer using Ollama.
    """

    if ollama_client is None:
        raise RuntimeError(
            "Ollama client not initialized. "
            "Set LLM_PROVIDER='ollama' at startup."
        )

    try:
        response = ollama_client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt.strip(),
                },
                {
                    "role": "user",
                    "content": user_prompt.strip(),
                },
            ],
        )

        answer = response["message"]["content"].strip()

        if not answer:
            raise RuntimeError(
                "Ollama returned an empty response."
            )

        return answer

    except Exception as e:
        logger.exception(
            "Failed to generate answer with Ollama."
        )

        raise RuntimeError(
            f"Failed to generate answer using Ollama: {e}"
        ) from e


# ---------------------------------------------------------------------------
# Gemini implementation
# ---------------------------------------------------------------------------

def _generate_with_gemini(
    system_prompt: str,
    user_prompt: str,
) -> str:
    """
    Generate an answer using the Google Gemini API.
    """

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set. "
            "Set it to use Gemini as the LLM provider."
        )

    if gemini_client is None:
        raise RuntimeError(
            "Gemini client not initialized. "
            "Set LLM_PROVIDER='gemini' and GEMINI_API_KEY at startup."
        )

    try:
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_prompt.strip(),
            config=types.GenerateContentConfig(
                system_instruction=system_prompt.strip(),
            ),
        )

        answer = response.text.strip()

        if not answer:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return answer

    except Exception as e:
        logger.exception(
            "Failed to generate answer with Gemini."
        )

        raise RuntimeError(
            f"Failed to generate answer using Gemini: {e}"
        ) from e