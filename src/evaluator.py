from defenitions import *

EVALUATOR_PROMPT = """
Ты технический менеджер.
На основе истории интервью оцени кандидата.

История:
{history}

Сформируй отчет:

1. Decision:
- Grade
- Hiring Recommendation
- Confidence Score

2. Technical Review:
- Confirmed Skills
- Knowledge Gaps (с правильными ответами)

3. Soft Skills:
- Clarity
- Honesty
- Engagement

4. Roadmap:
- Темы для изучения
"""

def evaluator(state: InterviewState) -> InterviewState:
    history_text = "\n".join(
        f"Q: {h['question']}\nA: {h['answer']}\nV: {h['verdict']}"
        for h in state["history"]
    )

    feedback = llm(
        system=EVALUATOR_PROMPT.format(history=history_text),
        user="Сформируй финальный фидбэк",
    )

    print("\n📊 FINAL FEEDBACK\n")
    print(feedback)

    return {"final_feedback": feedback}
