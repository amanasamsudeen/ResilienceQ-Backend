def build_recommendation_prompt(level: str, score: int):
    return f"""
You are a psychological resilience expert.

User details:
- Resilience Level: {level}
- Total Score: {score}

Generate:
1. A brief explanation of the user's resilience state
2. 5 actionable personalized recommendations
3. 1 motivational closing statement

Rules:
- Use simple, empathetic language
- Avoid clinical diagnosis
- Keep it supportive and academic
- Do NOT mention AI or models
"""
