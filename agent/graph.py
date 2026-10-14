import re
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from agent.state import AgentState
from agent.guardrails import validate_input, validate_output, contains_blocked_request
from agent.router import route_question
from rag.retriever import search_policy, answer_from_context
from tools.employee import get_employee
from tools.leave import get_leave_balance, create_leave_request
from tools.public_apis import call_public_api
from tools.api_client import PublicAPIError
from config import settings

def input_guardrail(state: AgentState):
    text = validate_input(state["user_input"])
    user_message = {"role": "user", "content": text}
    if contains_blocked_request(text):
        return {
            "user_input": text,
            "answer": "I can't provide system prompts, secrets, passwords, or API keys.",
            "messages": [user_message],
        }
    return {"user_input": text, "messages": [user_message]}

def router_node(state: AgentState):
    history = state.get("messages", [])[:-1]
    decision = route_question(state["user_input"], history)
    return {
        "intent": decision.intent,
        "employee_id": decision.employee_id,
        "resolved_input": decision.resolved_question,
        "api_service": decision.api_service,
        "api_query": decision.api_query,
    }

def policy_node(state: AgentState):
    question = state.get("resolved_input", state["user_input"])
    docs = search_policy(question)
    if not docs:
        return {"context": "", "answer": "I couldn't find this information in the available employee policies."}
    context = "\n\n".join(f"[Source: {d.metadata.get('source', 'unknown')}]\n{d.page_content}" for d in docs)
    return {"context": context, "answer": validate_output(answer_from_context(question, context))}

def employee_node(state: AgentState):
    result = get_employee(state.get("employee_id", "EMP001"))
    answer = (f"Employee ID: {result['employee_id']}\nName: {result['name']}\n"
              f"Department: {result['department']}\nDesignation: {result['designation']}")
    return {"tool_result": result, "answer": validate_output(answer)}

def leave_balance_node(state: AgentState):
    result = get_leave_balance(state.get("employee_id", "EMP001"))
    answer = f"You have {result['annual_leave']} annual leave days and {result['sick_leave']} sick leave days remaining."
    return {"tool_result": result, "answer": validate_output(answer)}

def leave_request_node(state: AgentState):
    question = state.get("resolved_input", state["user_input"])
    dates = re.findall(r"\d{4}-\d{2}-\d{2}", question)
    if len(dates) < 2:
        return {"answer": "Please provide two dates in YYYY-MM-DD format, for example: 2026-10-12 to 2026-10-14."}
    start_date, end_date = dates[:2]
    approved = interrupt({
        "message": f"Create leave request for {state.get('employee_id', 'EMP001')} from {start_date} to {end_date}?",
        "action": "create_leave_request",
    })
    if not approved:
        return {"approved": False, "answer": "Leave request was cancelled because approval was not provided."}
    result = create_leave_request(state.get("employee_id", "EMP001"), start_date, end_date)
    return {"approved": True, "tool_result": result,
            "answer": validate_output(f"Leave request {result['request_id']} was created successfully and is pending approval.")}

def general_node(state: AgentState):
    llm = ChatOllama(model=settings.llm_model, base_url=settings.ollama_base_url, temperature=0.2)
    response = llm.invoke([
        SystemMessage(content="You are an employee service assistant. Answer concisely. Do not invent company policy."),
        HumanMessage(content=state.get("resolved_input", state["user_input"])),
    ])
    return {"answer": validate_output(response.content)}

def public_api_node(state: AgentState):
    service = state.get("api_service", "")
    query = state.get("api_query", "")
    try:
        answer = call_public_api(service, query)
    except PublicAPIError as exc:
        answer = f"{service.title() or 'Public API'} lookup failed: {exc}"
    return {"answer": validate_output(answer)}

def output_guardrail(state: AgentState):
    answer = state.get("answer", "No answer was produced.")
    if any(token in answer for token in ["BEGIN PRIVATE KEY", "sk-", "AIza"]):
        answer = "I can't provide sensitive credentials or secrets."
    answer = validate_output(answer)
    return {"answer": answer, "messages": [AIMessage(content=answer)]}

def route_after_router(state: AgentState):
    return state["intent"]

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("input_guardrail", input_guardrail)
    graph.add_node("router", router_node)
    graph.add_node("policy", policy_node)
    graph.add_node("employee", employee_node)
    graph.add_node("leave_balance", leave_balance_node)
    graph.add_node("leave_request", leave_request_node)
    graph.add_node("public_api", public_api_node)
    graph.add_node("general", general_node)
    graph.add_node("output_guardrail", output_guardrail)
    graph.add_edge(START, "input_guardrail")
    graph.add_edge("input_guardrail", "router")
    graph.add_conditional_edges("router", route_after_router, {
        "policy": "policy", "employee": "employee", "leave_balance": "leave_balance",
        "leave_request": "leave_request", "public_api": "public_api", "general": "general",
    })
    for node in ["policy", "employee", "leave_balance", "leave_request", "public_api", "general"]:
        graph.add_edge(node, "output_guardrail")
    graph.add_edge("output_guardrail", END)
    return graph.compile(checkpointer=MemorySaver())
