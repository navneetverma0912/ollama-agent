from agent.graph import build_graph

def main():
    graph = build_graph()
    cases = [
        ("How many annual leaves do I have?", "12 annual"),
        ("What is the work from home policy?", "2 days"),
        ("What is my employee ID?", "EMP001"),
    ]
    passed = 0
    for index, (question, expected) in enumerate(cases, start=1):
        result = graph.invoke({"user_input": question}, config={"configurable": {"thread_id": f"eval-{index}"}})
        answer = result.get("answer", "")
        ok = expected.lower() in answer.lower()
        print(f"[{'PASS' if ok else 'FAIL'}] {question}\n  Answer: {answer}\n")
        passed += int(ok)
    print(f"Passed {passed}/{len(cases)} tests.")

if __name__ == "__main__":
    main()
