import logging
from defenitions import *

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s [critic]',
    handlers=[logging.StreamHandler()]
)

CRITIC_PROMPT = """
Ты — технический интервьюер. Твоя задача — оценить ответ кандидата на вопрос: "{question}"

Проанализируй ответ: "{answer}" и выбери один из трех вариантов вердикта:

1. VERDICT: COMPLETE
   - Если ответ верный и полностью раскрывает тему.
   - Твое действие: Напиши "APPROVED".

2. VERDICT: INCOMPLETE
   - Если ответ верный, но поверхностный или не затрагивает важные детали.
   - Твое действие: Сформулируй ОДИН короткий уточняющий вопрос, чтобы кандидат раскрыл тему.

3. VERDICT: WRONG
   - Если ответ вообще о другом, содержит грубые фактические ошибки или человек признался, что не знает.
   - Твое действие: Напиши, что ответ неверный, и кратко зафиксируй пробел в знаниях.

ФОРМАТ ОТВЕТА (строго):
Вердикт: [COMPLETE / INCOMPLETE / WRONG]
Комментарий: [Твой уточняющий вопрос или пояснение]
"""

def critic(state: InterviewState) -> InterviewState:
    logging.info("Оценка ответа...")
    
    current_question = state["questions"][state["current_index"]]
    current_answer = state["current_answer"]

    response = llm(
        system=CRITIC_PROMPT.format(question=current_question, answer=current_answer),
        user="Проанализируй ответ."
    )

    # Парсим ответ
    verdict = "COMPLETE"
    if "Вердикт: INCOMPLETE" in response:
        verdict = "INCOMPLETE"
    elif "Вердикт: WRONG" in response:
        verdict = "WRONG"

    comment = response.split("Комментарий:")[-1].strip()
    
    new_index = state["current_index"]
    approved = False

    # Логика переходов
    if verdict == "COMPLETE":
        logging.info("✅ Ответ принят полностью.")
        approved = True
        new_index += 1
    elif verdict == "WRONG":
        logging.info("❌ Ответ неверный. Переходим к следующей теме.")
        approved = True # Считаем "завершенным", чтобы роутер переключил вопрос
        new_index += 1
    else: # INCOMPLETE
        logging.info("⚠️ Ответ неполный. Требуется уточнение.")
        approved = False # Оставляем на текущем индексе

    return {
        "critique": comment,
        "approved": approved,
        "current_index": new_index,
        "history": state["history"] + [{
            "question": current_question,
            "answer": current_answer,
            "verdict": verdict,
            "critique": comment
        }],
    }