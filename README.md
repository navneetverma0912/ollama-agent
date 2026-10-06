# Employee Service Agent — Day 5

Local mini-hackathon project using Ollama + LangGraph + Chroma + Pydantic.

Features:
- Router
- Employee and leave tools
- RAG over company policy documents
- Multi-turn conversation context with per-thread LangGraph memory
- Persistent chat sessions and messages in SQLite, with a reopenable chat list
- Input/output guardrails
- Human approval for leave requests
- Local evaluation
- Optional Langfuse package/config

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Pull Ollama models:

```bash
ollama pull qwen3:4b
ollama pull nomic-embed-text
```

Build the vector database:

```bash
python rag/ingest.py
```

Run:

```bash
python app.py
```

Try:
- `What is the work from home policy?`
- `How many annual leaves do I have?`
- `What is my employee ID?`
- `Create a leave request from 2026-10-12 to 2026-10-14`

The last request pauses for human approval.

Run local evaluation:

```bash
python evaluation/test_agent.py
```

## Architecture

```text
User -> Input Guardrail -> Context-aware Router
                              |-> Policy -> Chroma RAG -> Ollama
                              |-> Employee -> Tool
                              |-> Leave Balance -> Tool
                              |-> Leave Request -> Human Approval -> Tool
                              |-> General -> Ollama
                                         |
                                 Output Guardrail
                                         |
                                        END
```

The router uses recent messages from the same thread to resolve follow-up questions
before routing them. Conversation checkpoints use in-memory storage, so they are
cleared when the API process restarts. Chat transcripts are separately stored in
the `chat_sessions` and `chat_messages` SQLite tables and remain viewable after a
restart. The current demo scopes chat history by the supplied employee ID
(`EMP001` by default); it does not yet provide authenticated user accounts.
