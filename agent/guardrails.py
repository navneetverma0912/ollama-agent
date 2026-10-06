from pydantic import BaseModel, Field

class UserInput(BaseModel):
    text: str = Field(min_length=2, max_length=1000)

class FinalAnswer(BaseModel):
    answer: str = Field(min_length=1, max_length=5000)

def validate_input(text: str) -> str:
    return UserInput(text=text).text.strip()

def validate_output(answer: str) -> str:
    return FinalAnswer(answer=answer).answer.strip()

def contains_blocked_request(text: str) -> bool:
    lowered = text.lower()
    blocked = [
        "reveal system prompt", "show system prompt",
        "ignore previous instructions", "give me api key", "give me password",
    ]
    return any(item in lowered for item in blocked)
