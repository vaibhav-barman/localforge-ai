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
            timeout=10
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
