import json
import re
import os
import logging
import hashlib
from datetime import datetime
import streamlit as st

# ── Environment Detection ────────────────────────────────────────
USE_API_MODEL = True
GROQ_API_KEY = None

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    USE_API_MODEL = True
except Exception:
    USE_API_MODEL = False

# ── Provider Imports ─────────────────────────────────────────────
if USE_API_MODEL:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    import ollama

# ── Centralized Model Configuration ─────────────────────────────
DEFAULT_MODEL_OLLAMA = "phi3"
DEFAULT_MODEL_GROQ = "openai/gpt-oss-120b"
DEFAULT_MODEL = DEFAULT_MODEL_GROQ if USE_API_MODEL else DEFAULT_MODEL_OLLAMA

# ── Lightweight LLM Call Logging ─────────────────────────────────
def _get_logger():
    """Create a file logger for LLM calls. Failures are silently ignored."""
    try:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        logger = logging.getLogger("llm_calls")
        if not logger.handlers:
            handler = logging.FileHandler(
                os.path.join(log_dir, "llm_calls.log"), encoding="utf-8"
            )
            handler.setFormatter(logging.Formatter("%(message)s"))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    except Exception:
        return None


def _log_call(model, prompt, response_text):
    """Log a single LLM call. Never raises."""
    try:
        logger = _get_logger()
        if logger:
            logger.info(
                "[%s] MODEL: %s | PROMPT_LEN: %d | RESPONSE: %s",
                datetime.now().isoformat(),
                model,
                len(prompt),
                response_text[:200].replace("\n", " "),
            )
    except Exception:
        pass  # logging must never break execution


# ── Provider Functions (private) ─────────────────────────────────
def _ollama_chat(prompt, model, temperature):
    """Plain-text call via Ollama."""
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": temperature},
    )
    return response["message"]["content"].strip()


def _api_chat(prompt, model, temperature):
    """Plain-text call via Groq API."""
    completion = groq_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return completion.choices[0].message.content.strip()


def _ollama_json_chat(prompt, model, temperature):
    """JSON-formatted call via Ollama."""
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        format="json",
        options={"temperature": temperature},
    )
    return response["message"]["content"]


def _api_json_chat(prompt, model, temperature):
    """JSON-formatted call via Groq API."""
    completion = groq_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    return completion.choices[0].message.content


# ── Central LLM Gateway ─────────────────────────────────────────
def _make_cache_key(prompt):
    """Create a short hash for Streamlit caching."""
    return hashlib.md5(prompt.encode()).hexdigest()


@st.cache_data(show_spinner=False)
def _cached_llm_chat(_cache_key, prompt, model, temperature):
    """Cached wrapper — _cache_key drives the cache, prompt is the real input."""
    if USE_API_MODEL:
        return _api_chat(prompt, model, temperature)
    else:
        return _ollama_chat(prompt, model, temperature)


def llm_chat(prompt, model=None, temperature=0.1):
    """
    Centralized plain-text LLM call.
    Routes to Ollama (local) or Groq (cloud) based on environment.
    All agents should use this instead of calling ollama.chat() directly.
    """
    model = model or DEFAULT_MODEL
    try:
        cache_key = _make_cache_key(prompt)
        result = _cached_llm_chat(cache_key, prompt, model, temperature)
        _log_call(model, prompt, result)
        return result
    except Exception as e:
        print(f"LLM Error: {e}")
        _log_call(model, prompt, f"ERROR: {e}")
        return "AI service temporarily unavailable."


# ── JSON LLM Gateway (existing logic preserved) ─────────────────
def safe_json_chat(prompt, fallback, model=None, max_retries=3):
    """
    Safely executes an LLM chat expecting JSON output.
    Retries automatically if the LLM produces invalid JSON.
    Falls back to regex extraction if standard parsing fails.
    """
    model = model or DEFAULT_MODEL

    prompt_appended = (
        prompt
        + '\n\nIMPORTANT: Return ONLY valid JSON.'
        + '\nDo not include explanations, markdown formatting, or text before or after the JSON object.'
        + '\nEscape any double quotes inside string values using \\".'
    )

    for attempt in range(max_retries):
        try:
            # temperature 0.1 to reduce hallucinated syntax errors
            if USE_API_MODEL:
                content = _api_json_chat(prompt_appended, model, 0.1)
            else:
                content = _ollama_json_chat(prompt_appended, model, 0.1)

            if not content.strip():
                continue

            # Debug: print raw LLM response
            print("RAW LLM RESPONSE:")
            print(content)

            _log_call(model, prompt_appended, content[:200])

            # Strip markdown code fences before parsing
            content = content.strip()
            content = re.sub(r"```json", "", content)
            content = re.sub(r"```", "", content)
            content = content.strip()

            # Try standard parse first
            try:
                return json.loads(content, strict=False)
            except json.JSONDecodeError:
                # Fallback: try to extract JSON object from the response
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    print("EXTRACTED JSON:")
                    print(match.group())
                    return json.loads(match.group(), strict=False)
                raise  # re-raise if no match found

        except json.JSONDecodeError as e:
            error_msg = f"JSON Parse Error on attempt {attempt+1}: {e}"
            print(error_msg)
            prompt_appended += f"\n\nERROR: Your previous response caused a JSON parsing error: {e}. Please fix the syntax and return valid JSON."
        except Exception as e:
            print(f"LLM General Error: {e}")
            break

    print("  Stopping...")
    return fallback
