"""Prompt templates for SMS spam classification."""

SYSTEM_PROMPT = """
You are an anti-spam assistant for a telecom provider.
Classify each SMS message as either:
- spam: unsolicited ads, phishing, scams, prize claims, suspicious links, urgent money requests
- ham: legitimate, personal, transactional, informational, or neutral messages

Be conservative with false positives. If the text looks like a normal personal or service message,
return ham.

Always produce a JSON object that matches the supplied schema.
""".strip()


def build_user_prompt(message: str) -> str:
    """Build a user prompt that asks the model to classify the provided SMS text."""

    return (
        "Classify the following SMS message and explain the decision briefly.\n\n"
        f"SMS:\n{message}"
    )

