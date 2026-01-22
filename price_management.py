import json

STATE_FILE = "state.json"

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def find_price(key):
    state = load_state()
    return state.get(key)

def update_price(key, price):
    state = load_state()
    state[key] = price  # update OR add
    save_state(state)

def update_if_changed(key, new_price):
    state = load_state()
    old_price = state.get(key)

    if old_price != new_price:
        state[key] = new_price
        save_state(state)
        return True  # changed

    return False  # no change
