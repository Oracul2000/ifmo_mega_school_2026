from langgraph.graph import StateGraph, END
from defenitions import *
from question_planner import plan_questions
from critic import critic
from evaluator import evaluator

def ask_question(state: InterviewState) -> InterviewState:
    idx = state.get("current_index", 0)
    questions = state.get("questions", [])

    if idx >= len(questions):
        return {"stop": True}

    # Логика отображения вопроса
    if state.get("critique") and not state.get("approved", True):
        print(f"\n🔍 Уточнение:\n{state['critique']}")
    else:
        print(f"\n❓ Вопрос {idx + 1}:")
        print(questions[idx])

    answer = input("👤 Ответ: ").strip()
    
    # Если ввели стоп — выходим немедленно
    if answer.lower().startswith("стоп"):
        print("🛑 Прерывание интервью...")
        return {"current_answer": "стоп", "stop": True}

    return {"current_answer": answer, "stop": False}

def router(state: InterviewState) -> str:
    # 1. Проверяем флаг стоп или пустые вопросы
    if state.get("stop") or state.get("current_answer", "").lower().startswith("стоп"):
        return "evaluator"
    
    # 2. Если мы пришли сюда из critic и ответ не одобрен — идем на уточнение
    if state.get("approved") is False:
        return "ask_question"
    
    # 3. Если мы в процессе и нет стопа — двигаемся по кругу
    # (LangGraph сам поймет, какой узел вызвать следующим по логике графа)
    return "next"

# --- Сборка графа ---
graph = StateGraph(InterviewState)

graph.add_node("plan_questions", plan_questions)
graph.add_node("ask_question", ask_question)
graph.add_node("critic", critic)
graph.add_node("evaluator", evaluator)

graph.set_entry_point("plan_questions")
graph.add_edge("plan_questions", "ask_question")

# Условный переход после ввода вопроса
graph.add_conditional_edges(
    "ask_question",
    router,
    {
        "evaluator": "evaluator",
        "next": "critic" # Если не стоп, идем анализировать
    }
)

# Условный переход после анализа критика
graph.add_conditional_edges(
    "critic",
    router,
    {
        "evaluator": "evaluator",
        "next": "ask_question" # После критика возвращаемся за новым вопросом (или уточнением)
    }
)

graph.add_edge("evaluator", END)
app = graph.compile()

if __name__ == "__main__":
    app.invoke({
        "resume": "Алекс. Backend Developer. Senior / Team Lead. Более 7 лет, эксперт. Уверенный в себе, требовательный",
        "questions": [],
        "current_index": 0,
        "current_answer": "",
        "critique": "",
        "approved": True,
        "history": [],
        "stop": False, # Обязательно инициализируем
        "internal_thoughts": "",
        "final_feedback": "",
    })