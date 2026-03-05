# learner_model.py
import json
import os
import re

DATA_FILE = "learner_data.json"

# --- Known mistake categories from mistake_agent ---
VALID_MISTAKE_CATEGORIES = [
    "Concept Confusion",
    "Logic Error",
    "Order Confusion",
    "Syntax/Base Missing",
    "General Error",
]


def normalize_mistake_key(raw):
    """
    Strip LLM noise from mistake classifications.
    E.g., '- Concept Confusion\n\nLong explanation...' → 'Concept Confusion'
    Also catches: "The answer is 'Concept Confusion'. ..." → 'Concept Confusion'
    """
    if not raw or not isinstance(raw, str):
        return "General Error"

    # Strip leading dashes, whitespace, and markdown formatting
    cleaned = raw.strip().lstrip("-").strip()

    # Pass 1: match a known category at the START of the string
    for category in VALID_MISTAKE_CATEGORIES:
        if cleaned.lower().startswith(category.lower()):
            return category

    # Pass 2: search for a known category ANYWHERE in the string
    for category in VALID_MISTAKE_CATEGORIES:
        if category.lower() in cleaned.lower():
            return category

    # If nothing matched, take only the first line and clean it
    first_line = cleaned.split("\n")[0].strip().rstrip(".")
    # Remove any trailing explanation after a common separator
    for sep in [" —", " -", ":", ";"]:
        if sep in first_line:
            first_line = first_line.split(sep)[0].strip()

    return first_line if first_line else "General Error"


def initialize_db():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        default_data = {
            "name": "Learner",
            "level": "Beginner",
            "goal": "",
            "topic_scores": {},
            "mistake_history": {},
            "progress_history": {},
            "current_focus": {
                "current_topic": "",
                "next_step": ""
            }
        }
        save_data(default_data)


def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        initialize_db()
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {}
            # Ensure all fields exist with safe defaults
            data.setdefault("name", "Learner")
            data.setdefault("level", "Beginner")
            data.setdefault("goal", "")
            data.setdefault("topic_scores", {})
            data.setdefault("mistake_history", {})
            data.setdefault("progress_history", {})
            data.setdefault("current_focus", {
                "current_topic": "",
                "next_step": ""
            })
            return data
    except Exception:
        return {
            "name": "Learner",
            "level": "Beginner",
            "goal": "",
            "topic_scores": {},
            "mistake_history": {},
            "progress_history": {},
            "current_focus": {
                "current_topic": "",
                "next_step": ""
            }
        }


def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")


# --- Legacy functions (kept for backward compat) ---


def update_score(topic, score):
    """Legacy: simple overwrite. Prefer update_progress() instead."""
    data = load_data()
    data["topic_scores"][topic] = score
    save_data(data)


def log_mistake(mistake_type):
    """Legacy: raw log. Prefer update_mistake() instead."""
    data = load_data()
    if mistake_type:
        key = normalize_mistake_key(mistake_type)
        count = data["mistake_history"].get(key, 0)
        data["mistake_history"][key] = count + 1
        save_data(data)


# --- New structured tracking functions ---


def update_mistake(mistake_type):
    """Normalize the key and increment the mistake count."""
    key = normalize_mistake_key(mistake_type)
    data = load_data()
    data["mistake_history"][key] = data["mistake_history"].get(key, 0) + 1
    save_data(data)


def update_progress(topic, score):
    """
    Only write if score > current stored score.
    Never overwrite higher mastery with a lower score.
    Also logs to progress_history.
    """
    data = load_data()
    current = data["topic_scores"].get(topic, 0)
    if score > current:
        data["topic_scores"][topic] = score

    # Always append to progress_history for trend tracking
    history = data["progress_history"].get(topic, [])
    history.append(score)
    data["progress_history"][topic] = history

    save_data(data)


def update_focus(topic, next_step):
    """Store the current learning focus from roadmap_agent output."""
    if not next_step:
        next_step = "Continue practicing this topic"
    data = load_data()
    data["current_focus"] = {
        "current_topic": topic or "",
        "next_step": next_step
    }
    save_data(data)


def update_level(level):
    """Update the learner's level."""
    data = load_data()
    data["level"] = level
    save_data(data)


def update_goal(goal):
    """Update the learner's learning goal."""
    data = load_data()
    data["goal"] = goal
    save_data(data)
