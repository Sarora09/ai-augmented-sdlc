from typing import Literal
from langchain_core.messages import SystemMessage

def get_decision_review_by_LLM(decision, decision_llm):
    input_for_decision = decision
    if input_for_decision not in ["approve", "reject"]:
        system_message_llm1 = SystemMessage(content=f"Review the {input_for_decision} and return either approve or reject")
        ai_decision = decision_llm.invoke([system_message_llm1])
        return ai_decision.content
    else:
        return input_for_decision

def make_decision_with_retries(
    decesion_llm,
    decision_text: str,
    max_retries: int = 3
) -> Literal["approve", "reject"]:
    for attempt in range(max_retries):
        decision = get_decision_review_by_LLM(decision_text, decesion_llm).lower()
        if "approve" in decision:
            return "approve"
        if "reject" in decision:
            return "reject"
    raise ValueError("LLM failed to produce a valid decision after retries.")