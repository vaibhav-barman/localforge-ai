import subprocess
import os
from pyflakes.api import checkPath

def get_next_solution_directory() -> str:
    """Scans workspace directory to determine and return the next sequential solution path folder."""
    base_workspace = "workspace"
    os.makedirs(base_workspace, exist_ok=True)
    
    counter = 1
    while True:
        target_dir = os.path.join(base_workspace, f"solution_{counter}")
        if not os.path.exists(target_dir):
            return target_dir
        counter += 1

def execute_generated_code(code_string: str, solution_dir: str) -> str:
    """Writes code to the unique solution directory and executes it via an isolated subprocess."""
    os.makedirs(solution_dir, exist_ok=True)
    file_path = os.path.join(solution_dir, "generated_code.py")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code_string)
        
    # --- STATIC CODE QUALITY ANALYSIS (LINTING) ---
    from io import StringIO
    warning_stream = StringIO()
    error_stream = StringIO()
    
    checkPath(file_path, reporter=import_reporter(warning_stream, error_stream))
    lint_warnings = warning_stream.getvalue()
    
    if lint_warnings:
        return f"CODE QUALITY WARNING:\n{lint_warnings}\nPlease remove unused imports or unused variables to make the codebase clean."
        
    try:
        # ENVIRONMENT FIX: Isolate environment copies to enforce windowless execution mode
        env_sandbox = os.environ.copy()
        env_sandbox["TK_SILENT_MODE"] = "1"
        env_sandbox["PYTHONUNBUFFERED"] = "1"
        
        result = subprocess.run(
            ["python3", "generated_code.py"],
            input="3\n", # Simulates a user typing '3' and hitting Enter
            capture_output=True,
            text=True,
            timeout=8,
            cwd=solution_dir,
            env=env_sandbox
        )

        
        if result.returncode == 0:
            return f"SUCCESS\nSTDOUT:\n{result.stdout}"
        else:
            return f"RUN-TIME ERROR:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            
    except subprocess.TimeoutExpired as e:
        # HARD PROCESS TERMINATION: Kills the frozen subprocess immediately to unlock your terminal
        if hasattr(e, 'process') and e.process:
            e.process.kill()
        return "TIMEOUT ERROR: Script execution timed out. This could be due to an unresolved infinite network loop or blocking GUI threads."

def save_qa_report(final_state: dict) -> None:
    """Generates and writes a comprehensive QA Validation Report markdown artifact."""
    target_dir = final_state["solution_dir"]
    report_path = os.path.join(target_dir, "qa_validation_report.md")
    
    report_content = f"""# 📑 QA Validation & Execution Report

## 📊 Build Telemetry Metrics
- **Target Folder Environment:** {target_dir}
- **Total Self-Correction Cycles:** {final_state.get('error_count', 0)}
- **Final System Status:** {"✅ PASSED" if "SUCCESS" in final_state.get('execution_logs', '') else "⚠️ TERMINATED WITH WARNINGS"}

## 💻 Code Linting & Static Analysis Logs
```text
{final_state.get('qa_analysis', 'No execution anomalies detected.')}
```

## 🖥️ Subprocess Run-Time Logs (stdout / stderr)
```text
{final_state.get('execution_logs', 'No runtime logs recorded.')}
```
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"💾 QA Validation Report successfully archived: {report_path}", flush=True)

def import_reporter(warning_stream, error_stream):
    from pyflakes.reporter import Reporter
    return Reporter(warning_stream, error_stream)
