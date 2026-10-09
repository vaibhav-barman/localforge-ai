import re
from langchain_ollama import ChatOllama
from src.state import AgentState
from src.ui import render_agent_header, run_progress_bar

# Adding context ceilings prevents open-weight models from hanging on long code generations
pm_model = ChatOllama(model="llama3.1:latest", temperature=0.2, num_predict=1024)
coder_model = ChatOllama(model="qwen2.5-coder:7b", temperature=0.1, num_predict=2048)
qa_analyzer_model = ChatOllama(model="llama3.2:3b", temperature=0.1, num_predict=512)


def product_manager_agent(state: AgentState) -> dict:
    """Transforms raw requirements into technical code specifications with live UI logging."""
    render_agent_header("Product Manager", "llama3.1:latest", "Analyzing Scope & Specs")
    run_progress_bar("Technical Architecture Guidelines")
    
    prompt = f"""You are a senior Product Manager. Translate this application requirement into a clean technical specification.
    Outline expected logic, modules, data shapes, and handling parameters. Do not write code.
    
    User Request: {state['user_request']}
    """
    response = pm_model.invoke(prompt)
    return {
        "specification": response.content,
        "iteration_history": state.get("iteration_history", []) + ["PM built requirements architecture specification."]
    }

def software_engineer_agent(state: AgentState) -> dict:
    """Generates structural python scripts with customized loop condition headers."""
    cycle_num = state.get('error_count', 0) + 1
    
    if cycle_num == 1:
        render_agent_header("Software Engineer", "qwen2.5-coder:7b", "Writing First Code Draft")
        run_progress_bar("Operational Python Architecture Script")
    else:
        render_agent_header("Software Engineer", "qwen2.5-coder:7b", f"Refactoring Code Structure (Cycle {cycle_num})")
        run_progress_bar("Targeted Bug Corrections Suite")

    feedback_context = ""
    if state.get("execution_logs") and "ERROR" in state["execution_logs"]:
        feedback_context = f"""
        CRITICAL BUG FIX REQUIRED: Your prior code failed execution.
        RAW RUNTIME ERROR: {state['execution_logs']}
        QA STRUCTURAL ANALYSIS AND FIX SUGGESTION: {state['qa_analysis']}
        Refactor the system code to address this fault cleanly.
        """

    prompt = f"""You are an elite Python Engineer. Build complete, runnable script solutions matching this architecture:
    {state['specification']}
    {feedback_context}
    CRITICAL: Output ONLY valid, clean executable Python code inside standard markdown code blocks (```python ... ```). Do not include any introductory conversation or chat.
    """
    response = coder_model.invoke(prompt)
    
    raw_content = response.content
    code_match = re.search(r"```python(.*?)```", raw_content, re.DOTALL)
    clean_code = code_match.group(1).strip() if code_match else raw_content.strip()

    return {
        "source_code": clean_code,
        "iteration_history": state.get("iteration_history", []) + [f"Engineer adjusted codebase structure (Cycle {cycle_num})."]
    }

def qa_tester_agent(state: AgentState) -> dict:
    """Executes code via local sandboxed folder, rendering active pipeline telemetry tests."""
    from src.tools import execute_generated_code
    
    render_agent_header("QA Tester", "Linter Suite & Subprocess Script Run", "Running Telemetry Audits")
    run_progress_bar("Pyflakes & Executable Diagnostics")
    
    logs = execute_generated_code(state["source_code"], state["solution_dir"])
    current_errors = state.get("error_count", 0)
    
    if "ERROR" in logs or "TIMEOUT" in logs or "WARNING" in logs:
        current_errors += 1
        print(f"\n[\033[91m⚠️ WARNING\033[0m] QA Telemetry Failed! Routing logs back to engineering loop.")
        
        analysis_prompt = f"""You are a Quality Assurance Automation Engineer. Analyze this python execution log error and briefly state exactly what went wrong and how to fix it in 2-3 sentences.
        Code written:\n{state['source_code']}\nExecution Failure Logs:\n{logs}"""
        analysis_response = qa_analyzer_model.invoke(analysis_prompt)
        qa_feedback = analysis_response.content
    else:
        qa_feedback = "No errors detected. Code works perfectly."
        
    return {
        "execution_logs": logs,
        "qa_analysis": qa_feedback,
        "error_count": current_errors,
        "iteration_history": state.get("iteration_history", []) + [f"QA validation executed: {'Passed' if 'SUCCESS' in logs else 'Failed. Retrying developer loop.'}."]
    }
