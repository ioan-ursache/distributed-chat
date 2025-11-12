import json

def encode_message(msg_type, text, sender=None):
    msg = {"type": msg_type, "text": text}
    if sender:
        msg["from"] = sender
    return json.dumps(msg) + "\n"

def decode_message(raw_data):
    try:
        return json.loads(raw_data)
    except json.JSONDecodeError:
        return None
