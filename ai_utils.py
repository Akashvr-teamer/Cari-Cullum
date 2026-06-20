"""Thin abstraction over free-tier LLM providers (Groq, Google Gemini).

Both providers offer no-credit-card free tiers as of mid-2026. Model names
on free tiers change fairly often — if a default model below starts
returning errors, swap it for whatever your provider's console currently
lists as free. Groq: https://console.groq.com — Gemini: https://aistudio.google.com
"""

DEFAULT_MODELS = {
    "Groq": "llama-3.3-70b-versatile",
    "Gemini": "gemini-2.5-flash",
}


class LLMError(Exception):
    pass


def call_groq(api_key, model, system_prompt, user_prompt, history=None, temperature=0.4):
    try:
        from groq import Groq
    except ImportError as e:
        raise LLMError("The 'groq' package isn't installed. Run: pip install groq") from e

    client = Groq(api_key=api_key)
    messages = [{"role": "system", "content": system_prompt}]
    for m in (history or []):
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_prompt})

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return resp.choices[0].message.content
    except Exception as e:  # noqa: BLE001 - surface provider errors plainly
        raise LLMError(f"Groq request failed: {e}") from e


def call_gemini(api_key, model, system_prompt, user_prompt, history=None, temperature=0.4):
    try:
        from google import genai
        from google.genai import types
    except ImportError as e:
        raise LLMError("The 'google-genai' package isn't installed. Run: pip install google-genai") from e

    client = genai.Client(api_key=api_key)
    contents = []
    for m in (history or []):
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=user_prompt)]))

    try:
        resp = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
            ),
        )
        return resp.text
    except Exception as e:  # noqa: BLE001
        raise LLMError(f"Gemini request failed: {e}") from e


def call_llm(provider, api_key, system_prompt, user_prompt, model=None, history=None, temperature=0.4):
    if not api_key:
        raise LLMError("No API key set. Add one in the sidebar to use the AI features.")
    model = model or DEFAULT_MODELS.get(provider)
    if provider == "Groq":
        return call_groq(api_key, model, system_prompt, user_prompt, history, temperature)
    if provider == "Gemini":
        return call_gemini(api_key, model, system_prompt, user_prompt, history, temperature)
    raise LLMError(f"Unknown provider: {provider}")
