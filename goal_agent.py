import ollama
import json
import llm_utils

def generate_learning_path(goal):
    prompt = f"""
    Act as an intelligent learning mentor.
    The learner's objective is: '{goal}'
    
    Provide a personalized learning path, generating structured JSON with the following exact keys. Do not use markdown inside keys.
    {{
        "personalized_learning_path": {{
            "recommended_topics": ["Topic 1", "Topic 2", "Topic 3"],
            "learning_order": "Explanation of why this order makes sense.",
            "prerequisites": ["Prereq 1", "Prereq 2", "None if none required"],
            "difficulty": "Beginner / Intermediate / Advanced",
            "estimated_time": "Time to become comfortable",
            "key_success_tip": "One critical tip for succeeding at this goal."
        }},
        "suggested_starting_topic": "The exact name of the first topic they should learn.",
        "weekly_milestones": {{
            "week_1_focus": "Specific goal for week 1",
            "week_2_focus": "Specific goal for week 2"
        }},
        "practice_recommendations": {{
            "platform": "Specific platform name and why",
            "project_idea": "One practical project idea",
            "real_world_app": "How this relates to real-world applications"
        }},
        "career_relevance": "Explain how this helps with placements, interviews, or industry jobs, prioritizing high-frequency topics."
    }}
    """
    
    fallback = {
        "personalized_learning_path": {
            "recommended_topics": ["Fundamentals", "Core Concepts"],
            "learning_order": "Start basic, move to advanced.",
            "prerequisites": ["None"],
            "difficulty": "Beginner",
            "estimated_time": "2 weeks",
            "key_success_tip": "Practice daily."
        },
        "suggested_starting_topic": "Fundamentals",
        "weekly_milestones": {
            "week_1_focus": "Understand the basics.",
            "week_2_focus": "Build a small project."
        },
        "practice_recommendations": {
            "platform": "LeetCode / HackerRank",
            "project_idea": "Simple CLI tool",
            "real_world_app": "Core logic in any application."
        },
        "career_relevance": "Foundational knowledge required for all technical interviews."
    }
    
    return llm_utils.safe_json_chat(prompt, fallback)
