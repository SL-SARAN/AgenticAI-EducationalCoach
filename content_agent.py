# content_agent.py
import ollama

def generate_explanation(topic, mistake_type):
    prompt = f"""
    Explain the concept of '{topic}' specifically addressing the mistake type '{mistake_type}'.
    Keep it concise (2-3 sentences).
    """
    try:
        response = ollama.chat(model='phi3', messages=[
             {'role': 'user', 'content': prompt}
        ])
        return response['message']['content']
    except:
        return "Review the basic concepts again."
