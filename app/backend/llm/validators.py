from typing import Any
from langchain_core.messages import HumanMessage, AIMessage
from app.backend.workflow.state import util_state


def validate_llm_response(response: Any, stage: str) -> str:
    content = getattr(response, "content", "").strip()
    if not content:
        raise ValueError(f"Empty response from LLM at stage: {stage} and Model is {util_state['current_model']}")
    return content

def prune_messages_user_assistant_only(messages) -> list:
    messages = [msg for msg in messages if isinstance(msg, (HumanMessage, AIMessage))]
    return messages[-2:];