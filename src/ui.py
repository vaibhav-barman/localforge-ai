import sys
import time
from datetime import datetime

def get_timestamp() -> str:
    """Returns the current real-time timestamp cleanly formatted."""
    return datetime.now().strftime("%H:%M:%S")

def render_agent_header(agent_name: str, model_name: str, status: str = "STARTING"):
    """Prints a styled status bar block tracking which local LLM is active."""
    colors = {
        "PRODUCT MANAGER": "\033[94m",   # Blue
        "SOFTWARE ENGINEER": "\033[92m",  # Green
        "QA TESTER": "\033[93m",          # Yellow
        "SYSTEM OVERSEER": "\033[95m"     # Magenta
    }
    reset = "\033[0m"
    color = colors.get(agent_name.upper(), "\033[97m")
    
    print(f"\n[{get_timestamp()}] {color}🤖 {agent_name} ({model_name}) ➔ Status: {status}{reset}", flush=True)
    print("-" * 65, flush=True)

def run_progress_bar(duration_label: str, iterations: int = 15):
    """Simulates a live progress loader stream tracking generation phases."""
    for i in range(iterations + 1):
        percent = int((i / iterations) * 100)
        bar = "█" * (i // 2) + "-" * (8 - (i // 2))
        sys.stdout.write(f"\r[{get_timestamp()}] ⏳ Generating {duration_label} [{bar}] {percent}% ")
        sys.stdout.flush()
        time.sleep(0.05)
    print("➔ Sent to local LLM context processing engine... 🚀", flush=True)
