import logging
from defenitions import *

logging.basicConfig(level=logging.INFO)

QUESTION_PLANNER_PROMPT = """
Ты технический интервьюер.
На основе резюме кандидата составь 5–10 технических вопросов.

Правила:
- Каждый вопрос строго по конкретному пункту резюме
- Один вопрос — один навык
- Запрещены общие вопросы
- Формат: нумерованный список
"""

def plan_questions(state: InterviewState) -> InterviewState:
    questions_text = llm(
        system=QUESTION_PLANNER_PROMPT,
        user=state["resume"],
    )

    questions = [
        q.strip().lstrip("0123456789. ")
        for q in questions_text.split("\n")
        if q.strip()
    ]

    return {
        "questions": questions[1:],
        "current_index": 0,
        "difficulty": 1,
    }
