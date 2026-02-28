import ollama
import json
import urllib.parse
import llm_utils

def recommend_resources(topic, mistake_type, level):
    prompt = f"""
    Act as an intelligent learning coach.
    The learner studied '{topic}' (Level: {level}) and made a mistake related to: '{mistake_type}'.
    
    1. Analyze this mistake and provide `resource_advice` explaining WHICH TYPE of resource (Video, Tutorial, or Practice Problem) they should prioritize first and why.
    2. Create ONE highly specific practical exercise tailored to their weakness.
    
    Return strict JSON:
    {{
        "resource_advice": "Advice on whether to start with videos, tutorials, or practice, and why based on their mistake.",
        "targeted_practice": {{
            "task_description": "Practical exercise description",
            "skill_built": "The specific skill this practices",
            "hint": "A subtle hint"
        }}
    }}
    """
    
    fallback = {
        "resource_advice": "Start with a video tutorial to visually grasp the fundamental concept, then move to coding practice.",
        "targeted_practice": {
            "task_description": f"Write a simple function applying the core concept of {topic}.",
            "skill_built": "Basic Syntax & Logic",
            "hint": "Check the official Python documentation for standard examples."
        }
    }
    
    result = llm_utils.safe_json_chat(prompt, fallback)
        
    # Programmatically generate safe search links
    encoded_topic = urllib.parse.quote(topic)
    
    result["dynamic_links"] = [
        {
            "icon": "🎥",
            "title": "Watch Video Explanations",
            "url": f"https://www.youtube.com/results?search_query={encoded_topic}+programming+tutorial"
        },
        {
            "icon": "📘",
            "title": "Read Tutorials",
            "url": f"https://www.google.com/search?q={encoded_topic}+tutorial+programming+example"
        },
        {
            "icon": "💻",
            "title": "Practice Problems",
            "url": f"https://www.google.com/search?q=site:leetcode.com+OR+site:hackerrank.com+{encoded_topic}"
        },
        {
            "icon": "📖",
            "title": "Explore Documentation",
            "url": f"https://www.google.com/search?q={encoded_topic}+documentation+programming"
        }
    ]
    
    return result
