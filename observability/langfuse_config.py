import os

def langfuse_enabled():
    return os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"

def get_langfuse():
    if not langfuse_enabled():
        return None
    try:
        from langfuse import get_client
        return get_client()
    except Exception as exc:
        print(f"Langfuse is not available: {exc}")
        return None
