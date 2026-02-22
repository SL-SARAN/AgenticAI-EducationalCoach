# roadmap_agent.py
import ollama
import json
import learning_setup

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
            "decision": "READY TO ADVANCE",
            "reason": "Explain why they are ready and why '{next_topic}' is the right next step.",
            "next_step_advice": {{
                "next_topic": "{next_topic}",
                "action": "Start learning {next_topic}",
                "tip_or_challenge": "A specific preparation tip for {next_topic}"
            }},
            "resources": [
                {{
                    "title": "Preview: {next_topic}",
                    "type": "Video / Article",
                    "url": "Specific working URL",
                    "reason": "To prepare for the next concept"
                }}
            ]
        }}
        """
    else:
        prompt = f"""
        Act as an intelligent learning coach.
        The learner studied '{topic}' (Level: {level}) and scored {score}%.
        The learner mistake: '{mistake_type}'.

        Determine whether the learner should:
        B) Continue learning this topic
        C) Reinforce fundamentals before continuing

        Return a strict JSON object with this structure:
        {{
            "decision": "CONTINUE LEARNING" or "REINFORCE FUNDAMENTALS",
            "reason": "Why this decision was made",
            "next_step_advice": {{
                "next_topic": "{topic}",
                "action": "What specifically to practice",
                "tip_or_challenge": "An intermediate challenge (if Continuing) or simple practice step (if Reinforcing)"
            }},
            "resources": [
                {{
                    "title": "Resource Title",
                    "type": "Video / Article / Practice",
                    "url": "Specific working URL",
                    "reason": "Why useful for remediation"
                }}
            ]
        }}
        """
    
    try:
        response = ollama.chat(model='phi3', messages=[
             {'role': 'user', 'content': prompt}
        ], format='json')
        return json.loads(response['message']['content'])
    except Exception as e:
        print(f"Roadmap Error: {e}")
        return {
            "decision": "CONTINUE LEARNING",
            "reason": "Error generating plan.",
            "next_step_advice": {
                "next_topic": topic,
                "action": "Review core concepts",
                "tip_or_challenge": "Try writing the code by hand."
            },
            "resources": []
        }
