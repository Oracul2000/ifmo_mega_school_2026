from typing import TypedDict, List
from langgraph.graph import END
from mistralai import Mistral
import json

MISTRAL_API_KEY = "n73W1QZoSb8evq1ad7OCmwKy7oI0sZDk"
MODEL = "mistral-large-latest"

client = Mistral(api_key=MISTRAL_API_KEY)


class InterviewState(TypedDict):
    resume: str
    questions: List[str]
    current_index: int
    current_answer: str
    critique: str
    approved: bool
    history: List[dict]
    internal_thoughts: str
    difficulty: int
    final_feedback: str


def llm(system: str, user: str) -> str:
    r = client.chat.complete(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return r.choices[0].message.content.strip()


def log_turn(state: InterviewState):
    with open("interview_log.json", "a", encoding="utf-8") as f:
        json.dump(
            {
                "turn_id": len(state["history"]),
                "question": state["history"][-1]["question"],
                "user_answer": state["history"][-1]["answer"],
                "verdict": state["history"][-1]["verdict"],
                "internal_thoughts": state["internal_thoughts"],
            },
            f,
            ensure_ascii=False,
        )
        f.write("\n")
