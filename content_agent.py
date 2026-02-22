# content_agent.py
import ollama
import json

def generate_explanation(topic, mistake_type, user_level):
    if "None" in mistake_type or "Correct" in mistake_type:
        prompt = f"""
        You are an expert Computer Science Tutor.
        The student (Level: {user_level}) correctly answered a question on '{topic}'.
        
        Provide deep reinforcement in strict JSON format:
        {{
            "learning_focus": "Advanced optimization or deeper concept related to {topic}",
            "root_cause": "Great job! You demonstrated strong understanding.",
            "concept_explanation": "Briefly explain the underlying principle and one advanced nuance.",
            "code_snippet": "A short, optimized/advanced Python code example",
            "code_explanation": "Explanation of the advanced technique",
            "practical_tip": "A tip for writing production-quality code"
        }}
        """
    else:
        prompt = f"""
        You are an expert Computer Science Tutor. 
        The student (Level: {user_level}) made a mistake of type '{mistake_type}' in the topic '{topic}'.
        
        Provide comprehensive feedback in strict JSON format:
        {{
            "learning_focus": "The specific sub-concept they missed (e.g. 'Base case in recursion')",
            "root_cause": "Why students typically make this mistake (e.g. 'Confusing return values with print statements')",
            "concept_explanation": "A simple, clear explanation of the correct concept (2-3 sentences)",
            "code_snippet": "A short, correct Python code example demonstrating the concept",
            "code_explanation": "Line-by-line comments/explanation of the code snippet",
            "practical_tip": "One actionable tip to verify their code in future"
        }}
        """
    
    prompt += "\nDo not use markdown formatting in the JSON keys."
    try:
        response = ollama.chat(model='phi3', messages=[
             {'role': 'user', 'content': prompt}
        ], format='json')
        return json.loads(response['message']['content'])
    except Exception as e:
        print(f"Content Error: {e}")
        return {
            "learning_focus": f"{topic} Fundamentals",
            "root_cause": "Common logical error.",
            "concept_explanation": "Review the basic syntax and logic flow.",
            "code_snippet": f"# Example for {topic}\nprint('Hello World')",
            "code_explanation": "Standard example.",
            "practical_tip": "Trace your code manually."
        }
