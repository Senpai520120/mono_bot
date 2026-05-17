import json

FILE_NAME = "history.json"

def save_history(entry):
    try:
        with open(FILE_NAME, 'r') as f:
            history = json.load(f)
    except:
        history = []

    history.insert(0, entry)
    history = history[:10]

    with open(FILE_NAME, 'w') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)


def get_history():
    try:
        with open(FILE_NAME, 'r') as f:
            return json.load(f)
    except:
        return []


