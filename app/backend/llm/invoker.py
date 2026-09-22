import groq
from app.utils.timeout import run_with_timeout
from app.utils.model_loader import *
from app.backend.workflow.state import util_state

def _is_retryable_error(exception):
    return (isinstance(exception, (TimeoutError, groq.RateLimitError)) or 
            "429" in str(type(exception)) or 
            "RateLimitError" in str(type(exception)) or
            "tool_use_failed" in str(exception))

def invoke_messages_with_fallback_models(primary_model, messages):
    fallback_models = [business_analyst_llm, product_owner_llm, system_designer_llm, business_analyst_llm,
                        technical_analyst_llm, business_analyst_llm, technical_architect_llm,
                        software_developer1_llm, software_developer2_llm, software_lead_llm,
                        security_engineer_llm, qa_engineer_llm, qa_reviewer_llm, qa_lead_llm]
    fallback_models = [model for model in fallback_models if model != primary_model]
    all_models = [primary_model] + fallback_models
    
    last_error = None
    
    for model in all_models:
        try:
            response = run_with_timeout(model.invoke, args=(messages,), timeout_seconds=120)
            if not getattr(response, "content", "").strip():
                last_error = ValueError(f"Empty response content from model {model.model_name}")
                continue
            util_state["current_model"] = model
            return response
        except Exception as e:
            if _is_retryable_error(e):
                last_error = e
                continue
            else:
                raise
    if isinstance(last_error, TimeoutError):
        raise TimeoutError("All models timed out after 120 seconds")
    elif isinstance(last_error, ValueError):
        raise ValueError("All fallback models returned empty responses. Please try again.")
    else:
        raise RuntimeError("Rate limits exceeded for all models. Please come back later.")