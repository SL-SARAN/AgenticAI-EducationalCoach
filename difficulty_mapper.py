# difficulty_mapper.py

def map_level_to_difficulty(user_level):
    """
    Maps user proficiency level to internal difficulty prompt.
    """
    mapping = {
        "Beginner": "Easy",
        "Basic": "Easy-Medium",
        "Intermediate": "Medium",
        "Advanced": "Hard"
    }
    return mapping.get(user_level, "Medium")
