from datetime import datetime

conversation_history = []
MAX_HISTORY = 50


def store_message(role, message):
    """
    role: 'user' or 'assistant'
    message: text message
    """

    entry = {
        "role": role,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    conversation_history.append(entry)

    # Keep only last N messages
    if len(conversation_history) > MAX_HISTORY:
        conversation_history.pop(0)


def get_history():
    return conversation_history.copy()


def clear_history():
    conversation_history.clear()