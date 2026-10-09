import os
from src.graph import build_workflow
from src.tools import save_qa_report  # Import the new report function

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
    
    # --- NEW: ARTIFACT WRITING LAYER ---
    os.makedirs("workspace", exist_ok=True)
    
    # 1. Save the Product Manager Specification Document
    pm_spec_path = os.path.join("workspace", "product_specification.md")
    with open(pm_spec_path, "w", encoding="utf-8") as f:
        f.write(f"# 📋 Technical Product Specification\n\n**Original Request:** {user_prompt}\n\n{final_output['specification']}")
    print(f"💾 PM Specification Document archived: {pm_spec_path}")
    
    # 2. Save the Final Generated System Source Code File
    # (This is already saved inside src/agents.py via execute_generated_code, but good to confirm context)
    
    # 3. Save the QA Analysis Audit Report File
    save_qa_report(final_output)
    # ------------------------------------
    
    print("\n🎉 Build Pipeline Finished! Check your '/workspace' directory for all compiled assets.")

if __name__ == "__main__":
    main()
