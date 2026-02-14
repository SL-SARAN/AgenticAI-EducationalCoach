# resource_agent.py

def recommend_resources(topic):
    base_url = "https://www.google.com/search?q="
    query = f"learn {topic} python best resources"
    
    # Specific curated links could go here, but for now we generate search queries
    return [
        f"[Real Python: {topic}]({base_url}{topic}+real+python)",
        f"[GeeksforGeeks: {topic}]({base_url}{topic}+geeksforgeeks)",
        f"[Youtube: {topic} Crash Course]({base_url}{topic}+crash+course+youtube)"
    ]
