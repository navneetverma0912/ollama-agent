from agent.graph import build_graph
from langgraph.types import Command

def main():
    graph = build_graph()
    thread_id = "employee-demo-user-1"
    print("=" * 65)
    print("Employee Service Agent")
    print("Ollama + LangGraph + Chroma + Pydantic")
    print("Type 'exit' to quit.")
    print("=" * 65)
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        if not user_input:
            print("Please enter a question.")
            continue
        config = {"configurable": {"thread_id": thread_id}}
        try:
            result = graph.invoke({"user_input": user_input}, config=config)
            while "__interrupt__" in result:
                value = result["__interrupt__"][0].value
                print("\nAPPROVAL REQUIRED")
                print(value)
                decision = input("Approve? [y/N]: ").strip().lower()
                result = graph.invoke(Command(resume=decision in {"y", "yes"}), config=config)
            print(f"\nAgent: {result.get('answer', 'No answer was produced.')}")
        except Exception as exc:
            print(f"\nAgent error: {exc}")

if __name__ == "__main__":
    main()
