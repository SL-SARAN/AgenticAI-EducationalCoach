# question_agent.py
import ollama
import json

def generate_question(topic, difficulty):
    prompt = f"""
    Generate a multiple-choice question on the topic '{topic}' at a '{difficulty}' difficulty level.
    You must return a valid JSON object. Do not adding any markdown formatting.
    The JSON schema is:
    {{
        "question": "The question text",
        "options": {{
            "A": "Option A text",
            "B": "Option B text",
            "C": "Option C text",
            "D": "Option D text"
        }},
        "correct_answer": "A",
        "mistake_map": {{
            "A": "Mistake Type for A",
            "B": "Mistake Type for B",
            "C": "Mistake Type for C",
            "D": "Mistake Type for D"
        }}
    }}
    """
    
    try:
        response = ollama.chat(model='phi3', messages=[
            {'role': 'user', 'content': prompt}
        ], format='json')
        
        content = response['message']['content']
        return json.loads(content)
    except Exception as e:
        print(f"Error generating question: {e}")
        # Fallback question if AI fails
        return {
            "question": f"What is a key concept in {topic}?",
            "options": {"A": "Concept 1", "B": "Concept 2", "C": "Concept 3", "D": "Concept 4"},
            "correct_answer": "A",
            "mistake_map": {"A": "Correct", "B": "Wrong", "C": "Wrong", "D": "Wrong"}
        }
