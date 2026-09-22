from typing import Literal
from app.backend.workflow.state import State, util_state
from app.backend.llm.invoker import invoke_messages_with_fallback_models
from app.backend.llm.validators import validate_llm_response, prune_messages_user_assistant_only
from app.backend.llm.decision_maker import make_decision_with_retries
from app.utils.file_writer import create_and_write_file
from app.prompt.prompt_library import PROMPT_REGISTRY
from app.utils.model_loader import *

def no_opp_router(state: State, config):
    pass

def router(state: State, config):
    next_node = config['configurable'].get("next_node")
    if next_node:
        return next_node
    return "generate_user_stories"

def generate_user_stories(state:State) -> State:
    print("====generate_user_stories====")
    system_message = PROMPT_REGISTRY["system_message_generate_user_stories"].format_messages(
        input = util_state["initial_input"].content
    );
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(business_analyst_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "generate_user_stories")
    create_and_write_file("generate_user_stories", updated_messages, ai_response_object, util_state["current_model"]);
    return {"generate_user_stories": ai_valid_response_content, "messages": [ai_response_object]}

def product_owner_review(state:State) -> State:
    print("====product_owner_review====")
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_product_owner_review"].format_messages(
        user_story = state["generate_user_stories"]
    )
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(product_owner_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "product_owner_review")
    create_and_write_file("product_owner_review", updated_messages, ai_response_object, util_state["current_model"]);
    return {"product_owner_review":ai_valid_response_content, "messages": [ai_response_object]}

def human_loop_product_owner_review(state:State) -> State:
    print("====human_loop_product_owner_review====")
    return state

def decision_product_owner_review(state:State) -> State:
    print("====decision_product_owner_review====")
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_decision_product_owner_review"].format_messages(
        user_story=state["generate_user_stories"],
        human_review_details = state["human_loop_product_owner_review"]
    )
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(product_owner_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "decision_product_owner_review")
    create_and_write_file("decision_product_owner_review", updated_messages, ai_response_object, util_state["current_model"]);
    return {"decision_product_owner_review": ai_valid_response_content, "messages": [ai_response_object]}

def make_product_owner_review_decision(state:State) -> Literal["approve", "reject"]:
    return make_decision_with_retries(product_owner_llm, state["decision_product_owner_review"])
    
def create_design_docs(state:State) -> State:
    print("====create_design_docs====")
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_create_design_docs"].format_messages(
        user_story = state["generate_user_stories"],
        product_owner_review = state["product_owner_review"],
        human_review = state["human_loop_product_owner_review"]
    )
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(system_designer_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "create_design_docs")
    create_and_write_file("create_design_docs", updated_messages, ai_response_object, util_state["current_model"]);
    return {"create_design_docs": ai_valid_response_content, "messages": [ai_response_object]}

def revise_user_stories(state:State) -> State:
    print("====revise_user_stories====")
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_revise_user_stories"].format_messages(
        user_story = state["generate_user_stories"],
        design_document = state["create_design_docs"]
    )
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(business_analyst_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "revise_user_stories")
    create_and_write_file("revise_user_stories", updated_messages, ai_response_object, util_state["current_model"]);
    return {"revise_user_stories": ai_valid_response_content, "messages": [ai_response_object]}

def design_review(state:State) -> State:
    print("====design_review====")
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_design_review"].format_messages(
        design_document = state["create_design_docs"],
        user_story = state["revise_user_stories"]
    );
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(technical_architect_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "design_review")
    create_and_write_file("design_review", updated_messages, ai_response_object, util_state["current_model"]);
    return {"design_review": ai_valid_response_content, "messages": [ai_response_object]}

def human_loop_design_review(state:State) -> State:
    return state

def decision_design_review(state:State) -> State:
    print("====decision_design_review====")
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_decision_design_review"].format_messages(
        user_story = state["revise_user_stories"],
        design_document = state["create_design_docs"],
        human_review_details = state["human_loop_design_review"]
    )
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(technical_architect_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "decision_design_review")
    create_and_write_file("decision_design_review", updated_messages, ai_response_object, util_state["current_model"]);
    return {"decision_design_review": ai_valid_response_content, "messages": [ai_response_object]}

def make_design_review_decision(state:State) -> Literal["approve", "reject"]:
    return make_decision_with_retries(technical_architect_llm, state["decision_design_review"])
    
def generate_code(state:State) -> State:
    print("====generate_code====")
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_generate_code"].format_messages(
        design_document = state["create_design_docs"],
        user_story = state["revise_user_stories"]
    )
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(software_developer1_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "generate_code")
    create_and_write_file("generate_code", updated_messages, ai_response_object, util_state["current_model"]);
    return {"generate_code":ai_valid_response_content,"messages": [ai_response_object]}

def code_review(state:State) -> State:
    print("====code_review====")
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_code_review"].format_messages(
        code = state["generate_code"],
        design_document = state["create_design_docs"],
        user_story = state["revise_user_stories"]
    )
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(software_developer2_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "code_review")
    create_and_write_file("code_review", updated_messages, ai_response_object, util_state["current_model"]);
    return {"code_review":ai_valid_response_content, "messages": [ai_response_object]}

def human_loop_code_review(state:State) -> State:
    return state

def decision_code_review(state:State) -> State:
    print("====decision_code_review====")
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_decision_code_review"].format_messages(
        user_story = state["revise_user_stories"],
        design_document = state["create_design_docs"],
        code = state["generate_code"],
        human_review = state["human_loop_code_review"]
    )
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(software_lead_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "decision_code_review")
    create_and_write_file("decision_code_review", updated_messages, ai_response_object, util_state["current_model"]);
    return {"decision_code_review": ai_valid_response_content, "messages": [ai_response_object]}

def make_code_review_decision(state:State) -> Literal["approve","reject"]:
    return make_decision_with_retries(software_lead_llm,state["decision_code_review"])

def security_review(state:State) -> State:
    print("====security_review====")
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_security_review"].format_messages(
        code = state["generate_code"],
        design_document = state["create_design_docs"]
    )
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(security_engineer_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "security_review")
    create_and_write_file("security_review", updated_messages, ai_response_object, util_state["current_model"]);
    return {"security_review": ai_valid_response_content,"messages": [ai_response_object]}

def fix_code_after_code_review(state:State) -> State:
    print("====fix_code_after_code_review====")
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_fix_code_after_code_review"].format_messages(
        code = state["generate_code"], 
        code_review = state["code_review"]
    )
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(software_developer1_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "fix_code_after_code_review")
    create_and_write_file("fix_code_after_code_review", updated_messages, ai_response_object, util_state["current_model"]);
    return {"fix_code_after_code_review": ai_valid_response_content,"messages": [ai_response_object]}

def fix_code_after_security(state:State) -> State:
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_fix_code_after_security"].format_messages(
        code = state["fix_code_after_code_review"], 
        security_review = state["security_review"]
    )
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(software_developer1_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "fix_code_after_security")
    create_and_write_file("fix_code_after_security", updated_messages, ai_response_object, util_state["current_model"]);
    return {"fix_code_after_security": ai_valid_response_content,"messages": [ai_response_object]}

def write_test_cases(state:State) -> State:
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_write_test_cases"].format_messages(
        user_story = state["revise_user_stories"], 
        code = state["fix_code_after_security"]
    )
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(qa_engineer_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "write_test_cases")
    create_and_write_file("write_test_cases", updated_messages, ai_response_object, util_state["current_model"]);
    return {"write_test_cases":ai_valid_response_content,"messages": [ai_response_object]}

def test_cases_review(state:State) -> State:
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_test_cases_review"].format_messages(
        test_cases= state["write_test_cases"], 
        code= state["fix_code_after_security"], 
        user_story= state["revise_user_stories"]
    )

    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(qa_reviewer_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "test_cases_review")
    create_and_write_file("test_cases_review", updated_messages, ai_response_object, util_state["current_model"]);
    return {"test_cases_review": ai_valid_response_content,"messages": [ai_response_object]}

def human_loop_test_cases_review(state:State) -> State:
    return state

def decision_test_cases_review(state:State) -> State:
    print("====decision_test_cases_review====")
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_decision_test_cases_review"].format_messages(
        user_story = state["revise_user_stories"],
        design_document = state["create_design_docs"],
        code = state["fix_code_after_security"],
        human_review_details = state["human_loop_test_cases_review"]
    )
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(qa_lead_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "decision_test_cases_review")
    create_and_write_file("decision_test_cases_review", updated_messages, ai_response_object, util_state["current_model"]);
    return {"decision_test_cases_review": ai_valid_response_content,"messages": [ai_response_object]}

def make_test_cases_review_decision(state:State) -> Literal["approve", "reject"]:
    return make_decision_with_retries(qa_lead_llm, state["decision_test_cases_review"])
    
def fix_test_cases(state:State) -> State:
    print("====fix_test_cases====")
    state["messages"] = prune_messages_user_assistant_only(state["messages"])
    system_message = PROMPT_REGISTRY["system_message_fix_test_cases"].format_messages(
        test_cases = state["write_test_cases"], 
        review_feedback = state["test_cases_review"], 
        code = state["fix_code_after_security"],
        user_story = state["revise_user_stories"]
    )
    updated_messages = state["messages"] + system_message;
    ai_response_object = invoke_messages_with_fallback_models(qa_engineer_llm, updated_messages);
    ai_valid_response_content = validate_llm_response(ai_response_object, "fix_test_cases")
    create_and_write_file("fix_test_cases", updated_messages, ai_response_object, util_state["current_model"]);
    return {"fix_test_cases": ai_valid_response_content,"messages": [ai_response_object]}