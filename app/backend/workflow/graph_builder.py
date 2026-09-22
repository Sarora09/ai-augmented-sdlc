from langgraph.graph import StateGraph, START, END
from app.backend.workflow.state import State
from app.backend.workflow.nodes import *

def build_graph():
    # Build workflow
    code_review_builder = StateGraph(State)

    # Add the nodes
    code_review_builder.add_node("router", no_opp_router)
    code_review_builder.add_node("generate_user_stories", generate_user_stories)
    code_review_builder.add_node("product_owner_review", product_owner_review)
    code_review_builder.add_node("human_loop_product_owner_review", human_loop_product_owner_review)
    code_review_builder.add_node("decision_product_owner_review", decision_product_owner_review)
    code_review_builder.add_node("create_design_docs", create_design_docs)
    code_review_builder.add_node("revise_user_stories", revise_user_stories)
    code_review_builder.add_node("design_review", design_review)
    code_review_builder.add_node("human_loop_design_review", human_loop_design_review)
    code_review_builder.add_node("decision_design_review", decision_design_review)
    code_review_builder.add_node("generate_code", generate_code)
    code_review_builder.add_node("code_review", code_review)
    code_review_builder.add_node("human_loop_code_review", human_loop_code_review)
    code_review_builder.add_node("decision_code_review", decision_code_review)
    code_review_builder.add_node("security_review", security_review)
    code_review_builder.add_node("fix_code_after_code_review", fix_code_after_code_review)
    code_review_builder.add_node("fix_code_after_security", fix_code_after_security)
    code_review_builder.add_node("write_test_cases", write_test_cases)
    code_review_builder.add_node("test_cases_review", test_cases_review)
    code_review_builder.add_node("human_loop_test_cases_review", human_loop_test_cases_review)
    code_review_builder.add_node("decision_test_cases_review", decision_test_cases_review)
    code_review_builder.add_node("fix_test_cases", fix_test_cases)

    # Add edges to connect nodes
    code_review_builder.add_edge(START, "router")
    code_review_builder.add_conditional_edges("router", router, 
                                              {
                                                  "human_loop_product_owner_review": "human_loop_product_owner_review",
                                                  "human_loop_design_review": "human_loop_design_review",
                                                  "human_loop_code_review": "human_loop_code_review",
                                                  "human_loop_test_cases_review": "human_loop_test_cases_review",
                                                  "generate_user_stories": "generate_user_stories"    
                                              })
    code_review_builder.add_edge("generate_user_stories", "product_owner_review")
    code_review_builder.add_edge("product_owner_review", "human_loop_product_owner_review")
    code_review_builder.add_edge("human_loop_product_owner_review", "decision_product_owner_review")
    code_review_builder.add_conditional_edges(
        "decision_product_owner_review", make_product_owner_review_decision, {
            "approve": "create_design_docs", 
            "reject": "generate_user_stories"
            }
    )
    code_review_builder.add_edge("create_design_docs", "revise_user_stories")
    code_review_builder.add_edge("revise_user_stories", "design_review")
    code_review_builder.add_edge("design_review", "human_loop_design_review")
    code_review_builder.add_edge("human_loop_design_review", "decision_design_review")
    code_review_builder.add_conditional_edges(
        "decision_design_review", make_design_review_decision, {
            "approve": "generate_code", 
            "reject": "revise_user_stories"
            }
    )
    code_review_builder.add_edge("generate_code", "code_review")
    code_review_builder.add_edge("code_review", "human_loop_code_review")
    code_review_builder.add_edge("human_loop_code_review", "decision_code_review")
    code_review_builder.add_conditional_edges(
        "decision_code_review", make_code_review_decision, {
            "approve": "security_review", 
            "reject": "generate_code"
            }
    )
    code_review_builder.add_edge("security_review", "fix_code_after_code_review")
    code_review_builder.add_edge("fix_code_after_code_review", "fix_code_after_security")
    code_review_builder.add_edge("fix_code_after_security", "write_test_cases")
    code_review_builder.add_edge("write_test_cases", "test_cases_review")
    code_review_builder.add_edge("test_cases_review", "human_loop_test_cases_review")
    code_review_builder.add_edge("human_loop_test_cases_review", "decision_test_cases_review")
    code_review_builder.add_conditional_edges(
        "decision_test_cases_review", make_test_cases_review_decision, {
            "approve": "fix_test_cases", 
            "reject": "write_test_cases"
            }
    )
    code_review_builder.add_edge("fix_test_cases", END)

    code_review_graph = code_review_builder.compile()

    return code_review_graph