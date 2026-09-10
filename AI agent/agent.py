from google import genai
from config import GEMINI_API_KEY
from tools import calculator, get_current_time
from memory import save_message, get_recent_messages

client = genai.Client(api_key=GEMINI_API_KEY)


def ask_agent(user_id, user_message):
    previous_messages = get_recent_messages(user_id)

    conversation = ""
    for role, message in previous_messages:
        conversation += f"{role}: {message}\n"

    prompt = f"""
    You are a helpful personal assistant.

    Here is the recent conversation:
    {conversation}

    Current user message:
    {user_message}

    Answer the user naturally.
    Use the available tools when necessary.
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={
            "tools": [
                calculator,
                get_current_time,
            ]
        },
    )

    answer = response.text

    save_message(user_id, "user", user_message)
    save_message(user_id, "assistant", answer)

    return answer