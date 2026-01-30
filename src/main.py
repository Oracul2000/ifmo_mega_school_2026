from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from mistralai import Mistral

from defenitions import *
from question_planner import *


# -------------------------
# Ask Question
# -------------------------
def ask_question(state: InterviewState) -> InterviewState:
    print(state["current_index"])
    idx = state["current_index"]

    if idx >= len(state["questions"]):
        return {}

    question = state["questions"][idx]
    print(f"\n❓ Вопрос {idx + 1}/{len(state['questions'])}:")
    print(question)

    answer = input("👤 Ответ: ")

    return {"current_answer": answer}


# -------------------------
# Critic
# -------------------------
def critic(state: InterviewState) -> InterviewState:
    print("\n🔍 Evaluating answer")

    critique = llm(
        system=(
            "Ты критик технических ответов.\n"
            "Если ответ корректный и по существу — напиши 'APPROVED'.\n"
            "Если нет — укажи, что именно не так."
        ),
        user=(
            f"ВОПРОС:\n{state['questions'][state['current_index']]}\n\n"
            f"ОТВЕТ:\n{state['current_answer']}"
        ),
    )

    approved = "APPROVED" in critique.upper()
    
    new_index = state["current_index"]
    if approved:
        new_index += 1

    return {
        "critique": critique,
        "approved": approved,
        "current_index": new_index,
        "history": state["history"]
        + [{
            "question": state["questions"][state["current_index"]],
            "answer": state["current_answer"],
            "critique": critique,
        }],
    }


# -------------------------
# Router
# -------------------------
def router(state: InterviewState) -> str:
    if state["approved"]:
        print("✅ Ответ принят")
        if state["current_index"] >= len(state["questions"]):
            return END
        return "ask_question"
    else:
        print("❌ Ответ не принят")
        print("📌 Комментарий:", state["critique"])
        return "ask_question"


# -------------------------
# Graph
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


# -------------------------
# Run
# -------------------------
app.invoke(
    {
        "resume": """Backend ML Engineer.
Разработал модель классификации сообщений клиентов.
Внедрил RAG-пайплайн.
Оптимизировал инференс LLM в продакшене.""",
        "questions": [],
        "current_index": 0,
        "current_answer": "",
        "critique": "",
        "approved": False,
        "history": [],
    }
)
