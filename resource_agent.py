import ollama
import json

def recommend_resources(topic, mistake_type, level):
    prompt = f"""
    Act as an intelligent learning coach.
    Recommend strictly 3 high-quality learning resources (1 visual video, 1 tutorial article, 1 interactive practice platform) for '{topic}' (Level: {level}) addressing mistake: '{mistake_type}'.
    Also create ONE specific practical exercise tailored to the learner's weakness.
    
    Return strict JSON:
    {{
        "smart_resources": [
            {{
                "title": "Resource Name",
                "why_useful": "Why this helps",
                "link": "Specific direct and working URL for {topic}"
            }}
        ],
        "targeted_practice": {{
            "task_description": "Practical exercise description",
            "skill_built": "The specific skill this practices",
            "hint": "A subtle hint"
        }}
    }}
    """
    
    try:
        response = ollama.chat(model='phi3', messages=[
             {'role': 'user', 'content': prompt}
        ], format='json')
        return json.loads(response['message']['content'])
    except Exception as e:
        print(f"Resource Error: {e}")
        return {
            "smart_resources": [
                {"title": f"{topic} Video", "why_useful": "Visual explanation", "link": "https://www.youtube.com"},
                {"title": f"{topic} Article", "why_useful": "Written instructions", "link": "https://www.wikipedia.org"},
                {"title": f"{topic} Practice", "why_useful": "Hands-on coding", "link": "https://www.hackerrank.com"}
            ],
            "targeted_practice": {
                "task_description": "Write a simple function using this concept.",
                "skill_built": "Basic Syntax",
                "hint": "Check the official Python docs."
            }
        }
