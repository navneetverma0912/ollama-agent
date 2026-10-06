from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4
from agent.graph import build_graph
from langgraph.types import Command
from database.conversation import (
    create_chat_session,
    get_chat_messages,
    get_chat_session,
    init_db,
    list_chat_sessions,
    save_chat_message,
)

app = FastAPI(title="Employee Service Agent API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

graph = build_graph()

class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1000)
    thread_id: Optional[str] = None
    employee_id: str = "EMP001"

class ApprovalRequest(BaseModel):
    thread_id: str
    approved: bool
    employee_id: str = "EMP001"

def format_result(result, thread_id):
    if "__interrupt__" in result:
        items = result["__interrupt__"]
        payload = items[0].value if items else {}
        return {"status":"approval_required","thread_id":thread_id,
                "answer":payload.get("message","Approval is required."),
                "approval":payload}
    return {"status":"completed","thread_id":thread_id,
            "answer":result.get("answer","I could not generate an answer."),
            "intent":result.get("intent"), "tool_result":result.get("tool_result")}

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/api/chat")
def chat(req: ChatRequest):
    tid = req.thread_id or str(uuid4())
    try:
        if req.thread_id:
            if get_chat_session(tid, req.employee_id) is None:
                raise HTTPException(404, "Chat not found.")
        else:
            title = req.message.strip()
            if len(title) > 60:
                title = title[:57].rstrip() + "..."
            create_chat_session(tid, req.employee_id, title)
        save_chat_message(tid, req.employee_id, "user", req.message)
        result = graph.invoke({"user_input":req.message,
                               "employee_id":req.employee_id},
                              {"configurable":{"thread_id":tid}})
        response = format_result(result, tid)
        save_chat_message(tid, req.employee_id, "assistant", response["answer"])
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/approval")
def approval(req: ApprovalRequest):
    try:
        if get_chat_session(req.thread_id, req.employee_id) is None:
            raise HTTPException(404, "Chat not found.")
        result = graph.invoke(Command(resume=req.approved),
                              {"configurable":{"thread_id":req.thread_id}})
        response = format_result(result, req.thread_id)
        save_chat_message(req.thread_id, req.employee_id, "assistant", response["answer"])
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/chats")
def chats(employee_id: str = "EMP001"):
    return list_chat_sessions(employee_id)

@app.get("/api/chats/{thread_id}")
def chat_history(thread_id: str, employee_id: str = "EMP001"):
    session = get_chat_session(thread_id, employee_id)
    if session is None:
        raise HTTPException(404, "Chat not found.")
    return {"chat": session, "messages": get_chat_messages(thread_id, employee_id)}

@app.get("/api/employee/{employee_id}")
def employee(employee_id: str):
    from tools.employee import get_employee
    data = get_employee(employee_id)
    if not data: raise HTTPException(404, "Employee not found")
    return data

@app.get("/api/leave-balance/{employee_id}")
def leave_balance(employee_id: str):
    from tools.leave import get_leave_balance
    return get_leave_balance(employee_id)

@app.on_event("startup")
def startup():
    init_db()