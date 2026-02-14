# learner_model.py
import json
import os

DATA_FILE = "learner_data.json"

def initialize_db():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "name": "Learner",
            "topic_scores": {},  # "Topic": score (0-100)
            "mistake_history": {} # "MistakeType": count
        }
        save_data(default_data)

def load_data():
    if not os.path.exists(DATA_FILE):
        initialize_db()
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")

def update_score(topic, score):
    data = load_data()
    current_score = data["topic_scores"].get(topic, 0)
    # Simple moving average or just update? Let's just update for now or max
    data["topic_scores"][topic] = score
    save_data(data)

def log_mistake(mistake_type):
    data = load_data()
    if mistake_type:
        count = data["mistake_history"].get(mistake_type, 0)
        data["mistake_history"][mistake_type] = count + 1
        save_data(data)
