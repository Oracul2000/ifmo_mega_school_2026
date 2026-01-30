import logging
from defenitions import *

logging.basicConfig(level=logging.INFO)

CRITIC_PROMPT = """
Ты Observer (Критик).

Проанализируй ответ кандидата.

Вопрос: {question}
Ответ: {answer}
История: {history}
Сложность: {difficulty}

Правила:
- Распознавай галлюцинации и бред
- Если ответ не по теме — WRONG
- Если частичный — INCOMPLETE
- Если полный — COMPLETE

ФОРМАТ:
[INTERNAL]
твои рассуждения

[FINAL]
Вердикт: COMPLETE / INCOMPLETE / WRONG
Комментарий: ...
"""

def critic(state: InterviewState) -> InterviewState:
    question = state["questions"][state["current_index"]]
    answer = state["current_answer"]
    
    if state.get("stop") or answer.lower().startswith("стоп"):
        return state

    response = llm(
        system=CRITIC_PROMPT.format(
            question=question,
            answer=answer,
            history=state["history"],
            difficulty=state["difficulty"],
        ),
        user="Проанализируй ответ",
    )

    internal = response.split("[FINAL]")[0].replace("[INTERNAL]", "").strip()
    final = response.split("[FINAL]")[1]

    verdict = "COMPLETE"
    if "INCOMPLETE" in final:
        verdict = "INCOMPLETE"
    elif "WRONG" in final:
        verdict = "WRONG"

    comment = final.split("Комментарий:")[-1].strip()

    # адаптация сложности
    difficulty = state["difficulty"]
    if verdict == "COMPLETE":
        difficulty = min(3, difficulty + 1)
    elif verdict == "WRONG":
        difficulty = max(1, difficulty - 1)

    approved = verdict != "INCOMPLETE"
    new_index = state["current_index"] + 1 if approved else state["current_index"]

    state["history"].append({
        "question": question,
        "answer": answer,
        "verdict": verdict,
        "critique": comment,
    })

    log_turn(state)

    return {
        "critique": comment,
        "approved": approved,
        "current_index": new_index,
        "internal_thoughts": internal,
        "difficulty": difficulty,
    }
