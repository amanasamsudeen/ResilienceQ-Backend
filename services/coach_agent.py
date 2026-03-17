def generate_coach_prompt(username, history, trend):

    if not history:
        return f"""
You are an AI resilience coach helping adolescents.

User Name: {username}

The user has no resilience assessment history yet.

Provide:
1. Encouragement to take the first assessment
2. 3 simple daily resilience-building activities
"""

    # latest record (DESC order)
    latest = history[0]

    # Format history for AI readability
    history_text = "\n".join([
        f"Score: {item.score}, Level: {item.level}"
        for item in history[:5]  # limit last 5
    ])

    prompt = f"""
You are an AI resilience coach helping adolescents.

User Name: {username}

Current Resilience Status:
Score: {latest.score}
Level: {latest.level}
Trend: {trend}

Recent Resilience History:
{history_text}

Tasks:
1. Analyze {username}'s resilience progress based on the trend.
2. Provide supportive and motivational coaching advice.
3. Suggest 3 simple daily resilience-building activities.

Guidelines:
- Be encouraging and positive
- Use simple language suitable for adolescents
- Address the user by their name

Response format:

Trend Insight:
Coaching Advice:
Daily Activities:
"""

    return prompt