# roadmap_agent.py

def generate_roadmap(topic, score):
    if score >= 80:
        return [
            f"Master internal implementation of {topic}",
            f"Solve hard LeetCode problems on {topic}",
            "Start learning the next topic"
        ]
    elif score >= 50:
        return [
            f"Review edge cases for {topic}",
            f"Practice standard {topic} problems",
            "Re-take the quiz tomorrow"
        ]
    else:
        return [
            f"Watch a foundational video on {topic}",
            "Write the code from scratch on paper",
            "Trace the execution flow manually"
        ]
