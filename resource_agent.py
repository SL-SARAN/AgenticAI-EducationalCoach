# resource_agent.py
import ollama
import json

def recommend_resources(topic, mistake_type, level):
    prompt = f"""
    Recommend 3 specific learning resources for '{topic}' (Level: {level}) addressing mistake: '{mistake_type}'.
    Also create ONE specific practice problem for them to try.
    
    Return strict JSON:
    {{
        "resources": [
            {{
                "title": "Resource Name",
                "type": "Video / Article / Practice",
                "url": "Specific URL",
                "reason": "Why this helps"
            }}
        ],
        "practice_problem": {{
            "title": "Problem Title",
            "description": "Short problem description",
            "skill_strengthened": "The specific skill this practices",
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
        base_url = "https://www.google.com/search?q="
        return {
            "resources": [],
            "practice_problem": {
                "title": f"Practice {topic}",
                "description": "Write a simple function using this concept.",
                "skill_strengthened": "Basic Syntax",
                "hint": "Check the docs."
            }
        }
