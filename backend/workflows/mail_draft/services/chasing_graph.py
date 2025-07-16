from langgraph.graph import StateGraph, END
from workflows.mail_draft.models.mail_graph_schema import AgentState
from workflows.mail_draft.services.nodes import (
    fetch_po_data_node,
    send_chase_email_node,
    filter_eligible_chasing_pos_node,
    determine_chase_email_type_node,
    update_po_status_and_log_sent_email_node,
    chase_po_iterator_node,
    regroup_chasing_pos_by_supplier_node,
    initialize_token_node
)

def should_continue_chasing(state: AgentState) -> str:
    """Conditional edge to decide if chasing should continue."""
    return "determine_chase_email_type" if state.get("current_po_group") else END

def create_chasing_workflow():
    """
    Creates and compiles the LangGraph workflow for chasing purchase orders.
    Focuses on drafting and logging first chase emails only.
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("fetch_po_data", fetch_po_data_node)
    workflow.add_node("initialize_token", initialize_token_node)
    workflow.add_node("filter_eligible_chasing_pos", filter_eligible_chasing_pos_node)
    workflow.add_node("regroup_chasing_by_supplier", regroup_chasing_pos_by_supplier_node)
    workflow.add_node("chase_po_iterator", chase_po_iterator_node)
    workflow.add_node("determine_chase_email_type", determine_chase_email_type_node)
    workflow.add_node("send_chase_email", send_chase_email_node)
    workflow.add_node("update_po_status_and_log_sent_email", update_po_status_and_log_sent_email_node)

    workflow.set_entry_point("fetch_po_data")
    workflow.add_edge("fetch_po_data", "initialize_token")
    workflow.add_edge("initialize_token", "filter_eligible_chasing_pos")
    workflow.add_edge("filter_eligible_chasing_pos", "regroup_chasing_by_supplier")
    workflow.add_edge("regroup_chasing_by_supplier", "chase_po_iterator")

    workflow.add_conditional_edges(
        "chase_po_iterator",
        should_continue_chasing,
        {
            "determine_chase_email_type": "determine_chase_email_type",
            END: END
        }
    )

    workflow.add_edge("determine_chase_email_type", "send_chase_email")
    workflow.add_edge("send_chase_email", "update_po_status_and_log_sent_email")
    workflow.add_edge("update_po_status_and_log_sent_email", "chase_po_iterator")

    return workflow.compile()
