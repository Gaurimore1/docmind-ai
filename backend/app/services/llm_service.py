# app/services/llm_service.py
#
# LLM service for DocMind AI.
#
# This service sends retrieved document context and the user's question
# to a locally running Ollama model and generates a grounded answer.
#
# Architecture:
#
#     User Question
#           ↓
#     Retrieved Chunks
#           ↓
#     Prompt
#           ↓
#     Ollama / phi3:mini
#           ↓
#     Answer


import logging
import os

from ollama import Client


# Module-level logger.
logger = logging.getLogger(__name__)


# Ollama model used by DocMind AI.
# phi3:mini is small and fast enough for local development.
MODEL_NAME = "phi3:mini"

# Ollama host — reads from the OLLAMA_URL environment variable so the
# Docker container can point to the Windows host via host.docker.internal.
# Falls back to localhost for direct (non-Docker) development.
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")

# Module-level client instance — created once at startup.
# Passing host= explicitly overrides Ollama's default localhost assumption,
# which is why the previous top-level chat() call failed inside Docker.
client = Client(host=OLLAMA_URL)


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
            If Ollama cannot generate an answer.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not context or not context.strip():
        raise ValueError("Context cannot be empty.")

    # System prompt defines DocMind's behaviour.
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

    # User prompt delivers the retrieved context and the question.
    # The context block is wrapped in clear delimiters so the model
    # cannot confuse document content with instructions.
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

    try:
        response = client.chat(
            model=MODEL_NAME,
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
        logger.exception("Failed to generate answer with Ollama.")

        raise RuntimeError(
            f"Failed to generate answer using Ollama: {e}"
        ) from e