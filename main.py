import os
from src.graph import build_workflow
from src.tools import get_next_solution_directory, save_qa_report
from src.ui import render_agent_header, get_timestamp

def main():
    print("\033[95m==============================================================\033[0m")
    print(f"🚀 [{get_timestamp()}] AgenticQA-Coder Framework Initialized Successfully")
    print("\033[95m==============================================================\033[0m")
    
    assigned_solution_dir = get_next_solution_directory()
    print(f"📁 [TARGET ENV] Isolated Environment: \033[93m{assigned_solution_dir}\033[0m\n", flush=True)
    
    user_prompt = input("Describe the Python script you want to build:\nPrompt > ")
    
    initial_state = {
        "user_request": user_prompt,
        "specification": "",
        "source_code": "",
        "execution_logs": "",
        "qa_analysis": "",
        "error_count": 0,
        "iteration_history": [],
        "solution_dir": assigned_solution_dir
    }
    
    app = build_workflow()
    
    render_agent_header("System Overseer", "LangGraph Compiler", "Compiling Agent Execution Paths")
    print(f"[{get_timestamp()}] ⚡ Compiling state machines and booting Ollama offline pipelines...", flush=True)
    
    final_output = app.invoke(initial_state)
    
    # --- SAVE ARTIFACTS ---
    target_folder = final_output["solution_dir"]
    os.makedirs(target_folder, exist_ok=True)
    
    pm_spec_path = os.path.join(target_folder, "product_specification.md")
    with open(pm_spec_path, "w", encoding="utf-8") as f:
        f.write(f"# 📋 Technical Product Specification\n\n**Original Request:** {user_prompt}\n\n{final_output['specification']}")
    
    save_qa_report(final_output)
    
    print("\n\033[92m==============================================================\033[0m")
    print(f"🎉 SUCCESS [{get_timestamp()}] Deployment complete! Target built inside {target_folder}", flush=True)
    print("\033[92m==============================================================\033[0m")

if __name__ == "__main__":
    main()
