def analyze_trend(history):

    if len(history) < 3:
        return "stable"

    scores = [item.score for item in history]

    avg_recent = sum(scores[:2]) / 2
    avg_previous = sum(scores[2:4]) / 2 if len(scores) >= 4 else scores[-1]

    if avg_recent > avg_previous:
        return "improving"

    elif avg_recent < avg_previous:
        return "declining"

    return "stable"