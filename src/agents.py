import re
from langchain_ollama import ChatOllama
from src.state import AgentState

# Initializing your specific local models
pm_model = ChatOllama(model="llama3.1:latest", temperature=0.2)
coder_model = ChatOllama(model="qwen2.5-coder:7b", temperature=0.1)
qa_analyzer_model = ChatOllama(model="llama3.2:3b", temperature=0.1)

def product_manager_agent(state: AgentState) -> dict:
    """Transforms raw requirements into technical code specifications."""
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
    """Generates structural python scripts or implements fixes derived from QA feedback logs."""
    feedback_context = ""
    if state.get("execution_logs") and "ERROR" in state["execution_logs"]:
        feedback_context = f"""
        CRITICAL BUG FIX REQUIRED: Your prior code failed execution.
        
        RAW RUNTIME ERROR:
        {state['execution_logs']}
        
        QA STRUCTURAL ANALYSIS AND FIX SUGGESTION:
        {state['qa_analysis']}
        
        Refactor the system code to address this fault cleanly.
        """

    prompt = f"""You are an elite Python Engineer. Build complete, runnable script solutions matching this architecture:
    {state['specification']}
    
    {feedback_context}
    
    CRITICAL: Output ONLY valid, clean executable Python code inside standard markdown code blocks (```python ... ```). Do not include any introductory conversation or chat.
    """
    response = coder_model.invoke(prompt)
    
    # Isolate raw text output inside standard python blocks
    raw_content = response.content
    code_match = re.search(r"```python(.*?)```", raw_content, re.DOTALL)
    clean_code = code_match.group(1).strip() if code_match else raw_content.strip()

    return {
        "source_code": clean_code,
        "iteration_history": state.get("iteration_history", []) + [f"Engineer adjusted codebase structure (Cycle {state.get('error_count', 0) + 1})."]
    }

def qa_tester_agent(state: AgentState) -> dict:
    """Executes code via local sandboxed shell, then leverages LLM reasoning to parse error output."""
    from src.tools import execute_generated_code
    
    # Step 1: Run the physical code execution check
    logs = execute_generated_code(state["source_code"])
    current_errors = state.get("error_count", 0)
    
    if "ERROR" in logs or "TIMEOUT" in logs:
        current_errors += 1
        
        # Step 2: Use the light 3B model to analyze what broke and provide clear feedback
        analysis_prompt = f"""You are a Quality Assurance Automation Engineer. Analyze this python execution log error and briefly state exactly what went wrong and how to fix it in 2-3 sentences.
        
        Code written:
        {state['source_code']}
        
        Execution Failure Logs:
        {logs}
        """
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