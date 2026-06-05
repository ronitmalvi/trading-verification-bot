sessions = {}

def get_state(phone):
    return sessions.get(phone, {}).get("state", "START")

def set_state(phone, state, **kwargs):
    sessions[phone] = {
        "state": state,
        **kwargs
    }

def get_session(phone):
    return sessions.get(phone, {})