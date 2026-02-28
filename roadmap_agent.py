import ollama
import json
import learning_setup
import llm_utils

def generate_roadmap(topic, score, mistake_type, level):
    is_success = score >= 80 or "None" in mistake_type or "Correct" in mistake_type
    
    # Calculate Next Topic
    try:
        topics = learning_setup.get_topics()
        current_idx = topics.index(topic)
        if current_idx < len(topics) - 1:
            next_topic = topics[current_idx + 1]
            progression_msg = f"The next logical topic is '{next_topic}'."
        else:
            next_topic = "Advanced Data Structures"
            progression_msg = "You have completed the core curriculum! Next is Advanced Data Structures."
    except ValueError:
        next_topic = "Next Module"
        progression_msg = "Proceed to the next module."

    if is_success:
        prompt = f"""
        Act as an intelligent learning coach.
        The learner studied '{topic}' (Level: {level}) and ACED the assessment with {score}%.
        Mistakes: None.
        
        CONTEXT: {progression_msg}

        The learner is READY TO ADVANCE.
        
        Determine the next logical step and return strict JSON:
        {{
            "learning_roadmap": [
                {{"action": "...", "why_it_matters": "...", "learn_here": "URL"}}
            ],
            "mastery_prediction": "Estimate mastery explicitly e.g., 90% - 95%.",
            "readiness_decision": "READY TO ADVANCE",
            "reason": "Explain why they are ready and why '{next_topic}' is the right next step.",
            "next_step_guidance": {{
                "next_step": "Suggest next topic '{next_topic}'",
                "explanation": "Explain why it logically follows"
            }}
        }}
        """
    else:
        prompt = f"""
        Act as an intelligent learning coach.
        The learner studied '{topic}' (Level: {level}) and scored {score}%.
        The learner mistake: '{mistake_type}'.

        Provide a structured roadmap returning strict JSON:
        {{
            "learning_roadmap": [
                {{"action": "Action 1", "why_it_matters": "Why Action 1 matters", "learn_here": "Specific URL tutorial/video"}},
                {{"action": "Action 2", "why_it_matters": "Why Action 2 matters", "learn_here": "Specific URL practice"}}
            ],
            "mastery_prediction": "Estimate mastery explicitly e.g., 85% - 90% after completing this roadmap",
            "readiness_decision": "Choose exactly ONE: CONTINUE LEARNING or REINFORCE FUNDAMENTALS",
            "reason": "Why this decision was made",
            "next_step_guidance": {{
                "next_step": "Suggest intermediate challenge (if Continuing) or simple corrective practice step (if Reinforcing)",
                "explanation": "Why this is the correct next step"
            }}
        }}
        """
        
    prompt += "\nDo not use markdown formatting in the JSON keys."
    
    fallback = {
        "learning_roadmap": [
            {"action": "Review core concepts", "why_it_matters": "Foundations are key", "learn_here": "https://www.google.com"}
        ],
        "mastery_prediction": "70-80%",
        "readiness_decision": "CONTINUE LEARNING",
        "reason": "Error generating plan.",
        "next_step_guidance": {
            "next_step": "Try the question again",
            "explanation": "Repetition builds retention"
        }
    }
    
    return llm_utils.safe_json_chat(prompt, fallback)
