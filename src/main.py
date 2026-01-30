from langgraph.graph import StateGraph, END
from defenitions import *
from question_planner import plan_questions
from critic import critic
from evaluator import evaluator

def ask_question(state: InterviewState) -> InterviewState:
    idx = state["current_index"]

    if idx >= len(state["questions"]):
        return {"stop": True}

    if state.get("critique") and not state["approved"]:
        print(f"\n🔍 Уточнение: {state['critique']}")
    else:
        print(f"\n❓ Вопрос {idx + 1}:")
        print(state["questions"][idx])

    answer = input("👤 Ответ: ")

    if answer.lower().startswith("стоп"):
        return {"stop": True}

    return {"current_answer": answer}


def router(state: InterviewState) -> str:
    if state.get("stop") or state["current_index"] >= len(state["questions"]):
        return "evaluator"
    return "ask_question"


graph = StateGraph(InterviewState)

graph.add_node("plan_questions", plan_questions)
graph.add_node("ask_question", ask_question)
graph.add_node("critic", critic)
graph.add_node("evaluator", evaluator)

graph.set_entry_point("plan_questions")
graph.add_edge("plan_questions", "ask_question")
graph.add_edge("ask_question", "critic")
graph.add_conditional_edges("critic", router)
graph.add_edge("evaluator", END)

app = graph.compile()

if __name__ == "__main__":
    app.invoke({
        "resume": "Backend ML Engineer. Оптимизировал инференс LLM.",
        "questions": [],
        "current_index": 0,
        "current_answer": "",
        "critique": "",
        "approved": True,
        "history": [],
        "internal_thoughts": "",
        "difficulty": 1,
        "final_feedback": "",
    })
