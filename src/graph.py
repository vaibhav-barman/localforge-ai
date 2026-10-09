from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.agents import product_manager_agent, software_engineer_agent, qa_tester_agent

def router_condition(state: AgentState):
    """Dynamic node router managing the self-correction cycle."""
    if "SUCCESS" in state["execution_logs"]:
        print("\n✨ QA METRIC PASSED: Executed with zero runtime anomalies.")
        return END
        
    if state["error_count"] >= 3:
        print("\n⚠️ SYSTEM BOUNDARY REACHED: Terminating cycle loops to maintain local compute threshold.")
        return END
        
    return "engineer"

def build_workflow():
    workflow = StateGraph(AgentState)
    
    # Establish graph workflow paths
    workflow.add_node("pm", product_manager_agent)
    workflow.add_node("engineer", software_engineer_agent)
    workflow.add_node("qa", qa_tester_agent)
    
    workflow.add_edge(START, "pm")
    workflow.add_edge("pm", "engineer")
    workflow.add_edge("engineer", "qa")
    
    # Conditional loop routing
    workflow.add_conditional_edges(
        "qa",
        router_condition,
        {
            "engineer": "engineer",
            END: END
        }
    )
    
    return workflow.compile()
