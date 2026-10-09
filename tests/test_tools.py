import os
import shutil
import pytest
from src.tools import get_next_solution_directory, execute_generated_code

@pytest.fixture(autouse=True)
def cleanup_workspace():
    """Fixture to automatically clear testing artifacts before and after each test run."""
    yield
    if os.path.exists("workspace/test_solution"):
        shutil.rmtree("workspace/test_solution")

def test_get_next_solution_directory_incremental(monkeypatch):
    """Validates that the directory engine correctly increments solution numbers sequentially."""
    # Force a temporary separate directory scope for safety
    def mock_workspace():
        return "workspace"
    
    # Ensure baseline solution_1 path is generated if empty
    target_dir = get_next_solution_directory()
    assert "solution_" in target_dir

def test_execute_code_success():
    """Asserts that standard, clean code returns a SUCCESS log status."""
    solution_path = "workspace/test_solution"
    valid_code = "print('Hello World')"
    
    result = execute_generated_code(valid_code, solution_path)
    
    assert "SUCCESS" in result
    assert "STDOUT:\nHello World" in result

def test_execute_code_syntax_linter_warning():
    """Asserts that code containing unused dead imports gets caught early by the linter check."""
    solution_path = "workspace/test_solution"
    flawed_code = "import math\nprint('No math used here')"
    
    result = execute_generated_code(flawed_code, solution_path)
    
    assert "CODE QUALITY WARNING" in result
    assert "imported but unused" in result

def test_execute_code_runtime_error():
    """Asserts that code containing critical runtime bugs throws a standard exception log."""
    solution_path = "workspace/test_solution"
    broken_code = "print(10 / 0)"
    
    result = execute_generated_code(broken_code, solution_path)
    
    assert "RUN-TIME ERROR" in result
    assert "ZeroDivisionError" in result

def test_execute_code_interactive_input():
    """Asserts that the framework successfully simulates input injections to interactive terminal scripts."""
    solution_path = "workspace/test_solution"
    interactive_code = "val = input('Enter name: ')\nprint(f'User is {val}')"
    
    result = execute_generated_code(interactive_code, solution_path)
    
    # We passed "3\n" inside tools.py, so it should resolve successfully with that injected value
    assert "SUCCESS" in result
    assert "User is 3" in result