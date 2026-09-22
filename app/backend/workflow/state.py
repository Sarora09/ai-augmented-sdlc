from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage

class UtilState(TypedDict):
    current_model: str
    uuid: str
    initial_input: HumanMessage

util_state: UtilState = {
    "current_model": "",
    "uuid": "",
    "initial_input": HumanMessage(content="")
}

roles_dictionary = {
    "messages": "messages",
    "generate_user_stories": "Business Analyst", 
    "product_owner_review": "Product Owner", 
    "human_loop_product_owner_review": "Human",
    "decision_product_owner_review": "Product Owner",
    "create_design_docs": "System Designer",
    "revise_user_stories": "Business Analyst",
    "design_review": "Technical Architect",
    "human_loop_design_review": "Human",
    "decision_design_review": "Technical Architect",
    "generate_code": "Software Developer 1",
    "code_review": "Software Developer 2",
    "human_loop_code_review": "Human",
    "decision_code_review": "Software Lead",
    "security_review": "Security Engineer",
    "fix_code_after_code_review": "Software Developer 1",
    "fix_code_after_security": "Software Developer 1",
    "write_test_cases": "QA Engineer",
    "test_cases_review": "QA Reviewer",
    "human_loop_test_cases_review": "Human",
    "decision_test_cases_review": "QA Lead",
    "fix_test_cases": "QA Engineer"
}

class State(TypedDict):
    messages: Annotated[list, add_messages]
    generate_user_stories: str
    product_owner_review: str
    human_loop_product_owner_review: str
    decision_product_owner_review: str
    create_design_docs: str
    revise_user_stories: str
    design_review: str
    human_loop_design_review: str
    decision_design_review: str
    generate_code: str
    code_review: str
    human_loop_code_review: str
    decision_code_review: str
    security_review: str
    fix_code_after_code_review: str
    fix_code_after_security: str
    write_test_cases: str
    test_cases_review: str
    human_loop_test_cases_review: str
    decision_test_cases_review: str
    fix_test_cases: str