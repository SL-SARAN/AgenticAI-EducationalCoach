# mistake_agent.py
import ollama

def classify_mistake(question, user_answer, correct_answer):
    prompt = f"""
    The student answered '{user_answer}' to the question: "{question}".
    The correct answer was '{correct_answer}'.
    Classify this mistake into one of these categories:
    - Concept Confusion
    - Logic Error
    - Order Confusion
    - Syntax/Base Missing
    
    Return ONLY the category name.
    """
    try:
        response = ollama.chat(model='phi3', messages=[
             {'role': 'user', 'content': prompt}
        ])
        return response['message']['content'].strip()
    except:
        return "General Error"
