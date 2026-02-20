def build_recommendation_prompt(level: str, score: int) -> str:
    return f"""
    You are a professional mental wellness assistant.
    Generate supportive, practical, and encouraging resilience guidance.
    
    Resilience Level: {level}
    Total Score: {score}
    """