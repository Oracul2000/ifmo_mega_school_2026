import logging

from defenitions import *

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s [question planner]',
    handlers=[
        logging.FileHandler('interview.log'),
        logging.StreamHandler()
    ]
)

QUESTION_PLANNER_PROMPT = '''
Ты технический интервьюер.
На основе резюме кандидата составь 5–10 технических вопросов, связаных с опытом работы кандидата.
Твоя задача понять, что именно делал человек и как именно он решал поставленные задачи, какими инструментами пользовался.

ПРИМЕР ЭТАЛОННОГО ВОПРОСА

Исходный пункт резюме:
"Разработал модель классификации сообщений клиентов."

Эталонный вопрос:
"Вы писали, что разработали модель классификации сообщений клиентов.
Расскажите: Какие модели вы рассматривали и почему выбрали финальную? Как была устроена предобработка данных? На какие метрики ориентировались и почему? Какие были основные сложности при внедрении?"

Исходный пункт резюме:
Провёл дообучение LLM на внутренних диалогах и базе знаний компании, что
повысило точность ответов и релевантность поддержке пользователей
Эталонный вопрос:
"Вы писали, что провели дообучение LLM на внутренних диалогах и базе знаний компании, что повысило точность ответов и релевантность поддержке пользователей.
Как проводилось чанкование исходного датасета? Кто выводил модель в прод? Какую модель выбрали для дообучения? Какие метрики использовались для оценки работы модели?"

❗ Правила:
- Каждый вопрос привязан к КОНКРЕТНОМУ пункту резюме
- Один вопрос — один пункт опыта
- Запрещены общие вопросы вида "расскажите подробнее"
- Формат — нумерованный список
'''

def plan_questions(state: InterviewState) -> InterviewState:
    logging.debug("Planning interview questions")

    questions_text = llm(
        system=(QUESTION_PLANNER_PROMPT),
        user=state["resume"],
    )
    
    logging.debug(questions_text)

    questions = questions_text.split("\n\n")

    return {
        "questions": questions,
        "current_index": 0,
    }
    
    
if __name__ == '__main__':
    logging.debug("Начало тестирования функции plan_questions")
    
    test_resume = """Иван Петров, Python разработчик с 3-х летним опытом.
    Основные навыки: Python, Django, FastAPI, PostgreSQL, Docker.
    Проекты:
    1. Разработка микросервисной архитектуры для банковского приложения
    2. Создание REST API для электронной коммерции
    3. Оптимизация запросов к базе данных, что уменьшило время ответа на 40%"""
    
    test_state = {"resume": test_resume}
    
    try:
        result = plan_questions(test_state)
        logging.info(f"Успешно сгенерировано {len(result['questions'])} вопросов")
        logging.info("Примеры вопросов:")
        for i, question in enumerate(result['questions'][:3], 1):
            logging.info(f"{i}. {question}")
        
        if len(result['questions']) == 0:
            logging.warning("Сгенерировано 0 вопросов! Проверьте формат ответа LLM.")
        elif len(result['questions']) < 5:
            logging.warning(f"Сгенерировано всего {len(result['questions'])} вопросов, ожидалось 5-10")
        
    except Exception as e:
        logging.error(f"Ошибка при тестировании: {e}", exc_info=True)
    
    logging.info("Тестирование завершено")

