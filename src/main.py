from typing import TypedDict, List
from langgraph.graph import StateGraph, END

from defenitions import *
from question_planner import *
from critic import critic # Импортируем новый модуль

# -------------------------
# Ask Question
# -------------------------
def ask_question(state: InterviewState) -> InterviewState:
    idx = state["current_index"]

    if idx >= len(state["questions"]):
        return {}

    # Если это уточняющий вопрос (approved был False в прошлом шаге)
    if state.get("critique") and not state.get("approved"):
        print(f"\n🔍 Уточнение: {state['critique']}")
    else:
        print(f"\n❓ Вопрос {idx + 1}/{len(state['questions'])}:")
        print(state["questions"][idx])

    answer = input("👤 Ответ: ")
    return {"current_answer": answer}


# -------------------------
# Router
# -------------------------
def router(state: InterviewState) -> str:
    # Если мы достигли конца списка вопросов
    if state["current_index"] >= len(state["questions"]):
        print("\n🏁 Интервью окончено. Спасибо!")
        return END
    
    # Если ответ был неполный (approved=False), возвращаемся в ask_question
    # Если ответ был COMPLETE или WRONG (approved=True), идем к следующему вопросу
    if not state["approved"]:
        return "ask_question"
    else:
        return "ask_question"


# -------------------------
# Graph Setup
# -------------------------
graph = StateGraph(InterviewState)

graph.add_node("plan_questions", plan_questions)
graph.add_node("ask_question", ask_question)
graph.add_node("critic", critic)

graph.set_entry_point("plan_questions")

graph.add_edge("plan_questions", "ask_question")
graph.add_edge("ask_question", "critic")

graph.add_conditional_edges(
    "critic",
    router,
    {
        "ask_question": "ask_question",
        END: END,
    },
)

app = graph.compile()

if __name__ == "__main__":
    app.invoke({
        "resume": "Backend ML Engineer. Оптимизировал инференс LLM.",
        "questions": [],
        "current_index": 0,
        "current_answer": "",
        "critique": "",
        "approved": False,
        "history": [],
    })