from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from mistralai import Mistral

MISTRAL_API_KEY = "n73W1QZoSb8evq1ad7OCmwKy7oI0sZDk"

client = Mistral(api_key=MISTRAL_API_KEY)
MODEL = "mistral-large-latest"


class InterviewState(TypedDict):
    resume: str
    questions: List[str]
    current_index: int
    current_answer: str
    critique: str
    approved: bool
    history: List[dict]


def llm(system, user):
    r = client.chat.complete(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return r.choices[0].message.content.strip()
