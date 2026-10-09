from src.graph import build_workflow

def main():
    print("==============================================")
    print("🚀 Local Agentic AI Software Engineering Loop")
    print("==============================================")
    
    user_prompt = input("Describe the Python script you want to build:\nPrompt > ")
    
    initial_state = {
        "user_request": user_prompt,
        "specification": "",
        "source_code": "",
        "execution_logs": "",
        "qa_analysis": "",
        "error_count": 0,
        "iteration_history": []
    }
    
    # Assemble compiled LangGraph
    app = build_workflow()
    
    print("\n⏳ Initializing local multi-agent context loops...")
    final_output = app.invoke(initial_state)
    
    print("\n================ SYSTEM TRACE ================")
    for event in final_output["iteration_history"]:
        print(f"✔ {event}")
    print("==============================================")
    
    print("\n💾 Script processing completed. Target saved: workspace/generated_code.py")

if __name__ == "__main__":
    main()
