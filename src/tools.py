import subprocess
import os
from pyflakes.api import checkPath

def execute_generated_code(code_string: str) -> str:
    """Writes code to an isolated file and executes it via a terminal subprocess to capture errors."""
    os.makedirs("workspace", exist_ok=True)
    file_path = os.path.join("workspace", "generated_code.py")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code_string)
        
    # --- NEW: STATIC CODE QUALITY ANALYSIS (LINTING) ---
    from io import StringIO
    warning_stream = StringIO()
    error_stream = StringIO()
    
    # Check for dead imports, unaccessed variables, or syntax anomalies
    checkPath(file_path, reporter=import_reporter(warning_stream, error_stream))
    lint_warnings = warning_stream.getvalue()
    
    if lint_warnings:
        return f"CODE QUALITY WARNING:\n{lint_warnings}\nPlease remove unused imports or unused variables to make the codebase clean."
    # ----------------------------------------------------
        
    try:
        result = subprocess.run(
            ["python3", file_path],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="workspace"
        )
        
        if result.returncode == 0:
            return f"SUCCESS\nSTDOUT:\n{result.stdout}"
        else:
            return f"RUN-TIME ERROR:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "TIMEOUT ERROR: The script execution took too long. Check for infinite loops."

# Quick helper reporter function for pyflakes formatting
def import_reporter(warning_stream, error_stream):
    from pyflakes.reporter import Reporter
    return Reporter(warning_stream, error_stream)

def save_qa_report(final_state: dict) -> None:
    """Generates and writes a comprehensive QA Validation Report markdown artifact to disk."""
    os.makedirs("workspace", exist_ok=True)
    report_path = os.path.join("workspace", "qa_validation_report.md")
    
    report_content = f"""# 📑 QA Validation & Execution Report

## 📊 Build Telemetry Metrics
- **Total Self-Correction Cycles:** {final_state.get('error_count', 0)}
- **Final System Status:** {"✅ PASSED" if "SUCCESS" in final_state.get('execution_logs', '') else "⚠️ TERMINATED WITH WARNINGS"}

## 💻 Code Linting & Static Analysis Logs
```text
{final_state.get('qa_analysis', 'No execution anomalies detected during build static linting.')}
```

## 🖥️ Subprocess Run-Time Logs (stdout / stderr)
```text
{final_state.get('execution_logs', 'No runtime logs recorded.')}
```

---
*Report generated autonomously by AgenticQA-Coder Framework.*
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print("💾 QA Validation Report successfully archived: workspace/qa_validation_report.md")
