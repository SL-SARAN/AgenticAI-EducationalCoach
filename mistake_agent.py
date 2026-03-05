# mistake_agent.py
from llm_utils import llm_chat

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
        response = llm_chat(prompt)
        return response
    except:
        return "General Error"
