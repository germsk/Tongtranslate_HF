import json

def norm(x):
    """Simplest possible normalizer for CrewOutput."""
    # 1. If CrewOutput with .raw -> parse that JSON
    if hasattr(x, "raw") and isinstance(x.raw, str):
        try:
            return json.loads(x.raw)
        except:
            return {}

    # 2. If already a dict
    if isinstance(x, dict):
        return x

    # 3. If it's a JSON string
    if isinstance(x, str):
        try:
            return json.loads(x)
        except:
            return {}

    # 4. Default fallback
    return {}