import os
from src.graph import build_workflow
from src.tools import get_next_solution_directory, save_qa_report  # Added directory scanner tool

def main():
    print("==============================================")
    print("🚀 Local Agentic AI Software Engineering Loop")
    print("==============================================")
    
    # Step 1: Calculate the next sequential destination folder name dynamically
    assigned_solution_dir = get_next_solution_directory()
    print(f"📁 Target Environment Destination for this session: {assigned_solution_dir}\n")
    
    user_prompt = input("Describe the Python script you want to build:\nPrompt > ")
    
    initial_state = {
        "user_request": user_prompt,
        "specification": "",
        "source_code": "",
        "execution_logs": "",
        "qa_analysis": "",
        "error_count": 0,
        "iteration_history": [],
        "solution_dir": assigned_solution_dir  # Save path parameter directly to shared state
    }
    
    # Assemble compiled LangGraph
    app = build_workflow()
    
    print("\n⏳ Initializing local multi-agent context loops...")
    final_output = app.invoke(initial_state)
    
    print("\n================ SYSTEM TRACE ================")
    for event in final_output["iteration_history"]:
        print(f"✔ {event}")
    print("==============================================")
    
    # --- SAVE ARTIFACTS DYNAMICALLY ---
    target_folder = final_output["solution_dir"]
    os.makedirs(target_folder, exist_ok=True)
    
    # 1. Save the Product Manager Specification Document
    pm_spec_path = os.path.join(target_folder, "product_specification.md")
    with open(pm_spec_path, "w", encoding="utf-8") as f:
        f.write(f"# 📋 Technical Product Specification\n\n**Original Request:** {user_prompt}\n\n{final_output['specification']}")
    print(f"💾 PM Specification Document archived: {pm_spec_path}")
    
    # 2. Save the QA Analysis Audit Report File
    save_qa_report(final_output)
    
    print(f"\n🎉 Build Pipeline Finished! Your complete session outputs are located inside: {target_folder}")

if __name__ == "__main__":
    main()
