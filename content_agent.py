import ollama
import json
import llm_utils

def generate_explanation(topic, mistake_type, user_level):
    if "None" in mistake_type or "Correct" in mistake_type:
        prompt = f"""
        Act as an intelligent learning coach and mentor.
        The learner (Level: {user_level}) studied '{topic}' and ACED the assessment.
        Mistake: {mistake_type}
        
        Provide structured learning guidance with deep personalization and pedagogical reasoning returning strictly JSON containing these fields:
        
        {{
            "learning_focus": "The advanced concept they are ready for next in {topic}",
            "knowledge_gap_profile": ["Identify 1-2 minor areas they could still polish or optimize if applicable"],
            "why_mistake_happens": "N/A - the student answered correctly, briefly praise them",
            "ai_explanation": {{
                "beginner_explanation": "An explanation of an advanced nuance related to the topic",
                "step_by_step_correction": "A step-by-step breakdown of how to think like a senior dev for this",
                "sample_code": "Advanced Python code example",
                "code_comments": "Explanation of the advanced technique",
                "practical_tip": "A tip for writing production-quality code"
            }},
            "why_this_matters": "Explain how mastering this advanced nuance helps in the real-world."
        }}
        """
    else:
        prompt = f"""
        Act as an intelligent learning coach and mentor.
        The learner (Level: {user_level}) studied '{topic}' and made a mistake.
        Detected mistake: {mistake_type}
        
        Provide structured learning guidance with deep personalization and pedagogical reasoning returning strictly JSON containing these fields:
        
        {{
            "learning_focus": "Identify the key concept the learner needs to improve based on {mistake_type}.",
            "knowledge_gap_profile": ["Identify recurring or potential conceptual weakness 1", "Identify recurring or potential conceptual weakness 2"],
            "why_mistake_happens": "Explain in simple terms why learners commonly make this mistake.",
            "ai_explanation": {{
                "beginner_explanation": "A beginner-friendly explanation correcting the mistake",
                "step_by_step_correction": "A step-by-step correction",
                "sample_code": "A short, correct Python code example demonstrating the concept",
                "code_comments": "Line-by-line comments/explanation of the code snippet",
                "practical_tip": "One practical tip to avoid this mistake in the future"
            }},
            "why_this_matters": "Explain how mastering this concept helps in real-world development and coding interviews."
        }}
        """
        
    prompt += "\nDo not use markdown formatting in the JSON keys."
    
    fallback = {
        "learning_focus": f"{topic} Fundamentals",
        "knowledge_gap_profile": ["Core concepts related to the problem"],
        "why_mistake_happens": "Common logical error.",
        "ai_explanation": {
            "beginner_explanation": "Review the basic syntax and logic flow.",
            "step_by_step_correction": "Trace your code logic.",
            "sample_code": f"# Example for {topic}\nprint('Hello World')",
            "code_comments": "Standard example.",
            "practical_tip": "Trace your code manually."
        },
        "why_this_matters": "Fundamental for all software engineering."
    }
    
    return llm_utils.safe_json_chat(prompt, fallback)
