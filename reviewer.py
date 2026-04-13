import os

from groq import Groq


SYSTEM_PROMPT = (
    "You are an expert document reviewer. Answer strictly based on the "
    "provided document excerpts. If the information is not present in the "
    "excerpts, clearly say so. Cite evidence in user-friendly language such as "
    "'Page 3' or 'the uploaded document states ...'. Never refer to internal "
    "chunk numbers, chunk IDs, embeddings, retrieval, or vector search."
)

MODEL_NAME = "llama-3.1-8b-instant"


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to your .env file.")
    return Groq(api_key=api_key)


def create_review_stream(query, chunks):
    client = _get_client()

    formatted_chunks = "\n\n---\n\n".join(
        _format_excerpt(excerpt, index) for index, excerpt in enumerate(chunks)
    )

    return client.chat.completions.create(
        model=MODEL_NAME,
        stream=True,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Document excerpts:\n"
                    f"{formatted_chunks}\n\n"
                    "Review task: "
                    f"{query}\n\n"
                    "Instructions:\n"
                    "- Base the answer only on the excerpts above.\n"
                    "- If the excerpts are insufficient, say what is missing.\n"
                    "- Cite pages when available.\n"
                    "- Do not mention internal labels like excerpt 1 or chunk 2."
                ),
            },
        ],
    )


def _format_excerpt(excerpt, index):
    content = excerpt.get("content", "").strip()
    page = excerpt.get("page")
    source = excerpt.get("source", "Uploaded PDF")
    page_label = f"Page {page}" if page is not None else "Page not available"

    return (
        f"Document excerpt {index + 1}\n"
        f"Source: {source}\n"
        f"Location: {page_label}\n"
        f"Text:\n{content}"
    )


def stream_review_response(stream):
    for chunk in stream:
        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta
        content = getattr(delta, "content", None)
        if content:
            yield content
