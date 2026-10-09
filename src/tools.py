import subprocess
import os

def execute_generated_code(code_string: str) -> str:
    """Writes code to an isolated file and executes it via a terminal subprocess to capture errors."""
    os.makedirs("workspace", exist_ok=True)
    file_path = os.path.join("workspace", "generated_code.py")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code_string)
        
    try:
        # 10-second safety cutoff to intercept infinite loops
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
