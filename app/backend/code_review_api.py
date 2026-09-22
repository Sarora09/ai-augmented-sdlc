from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.responses import Response
from app.backend import code_review_service
from app.exception.custom_exception import CustomException
from app.utils.logger import logger
from app.backend.middleware import custom_rate_limit_handler, verify_api_key, limiter
from slowapi.errors import RateLimitExceeded
import sys
import os

app = FastAPI(title="SDLC Life Cycle Agentic AI")

class InitialCodeReviewRequestState(BaseModel):
    human_message:str
    next_node: str
    thread_id: str

class ResumeCodeReviewState(BaseModel):
    state_dictionary: dict
    next_node: str
    thread_id: str

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

@app.post("/initiatecodereview", dependencies=[Depends(verify_api_key)])
@limiter.limit("10/minute")
def initiate_code_review(request: Request, body: InitialCodeReviewRequestState):
    if body.human_message == "":
        raise HTTPException(status_code = 422, detail = "human_message cannot be empty.")
    if body.human_message.isnumeric():
        raise HTTPException(status_code = 422, detail = "human_message cannot be numbers.")
    if body.next_node == "":
        raise HTTPException(status_code = 422, detail = "next_node cannot be empty.")
    if body.next_node.isnumeric():
        raise HTTPException(status_code = 422, detail = "next_node cannot be numbers.")
    if body.thread_id == "":
        raise HTTPException(status_code = 422, detail = "thread_id cannot be empty.")
    if body.thread_id.isnumeric():
        raise HTTPException(status_code = 422, detail = "thread_id cannot be numbers.")
    
    try:
        response = code_review_service.initiate_code_review(body.human_message, body.next_node, body.thread_id)
        return response
    except TimeoutError as timeout_error:
        logger.error(f"Timeout in initiate_code_review: {timeout_error}")
        raise HTTPException(status_code=504, detail="The request took too long to process. Please try again.")
    except Exception as _:
        error_detail = CustomException("Internal Server Error", error_details=sys.exc_info())
        logger.error(f"Error in initiate_code_review: {error_detail}")
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.")
    
@app.post("/resumecodereview", dependencies=[Depends(verify_api_key)])
@limiter.limit("10/minute")
def resume_code_review(request: Request, body: ResumeCodeReviewState):
    if body.next_node == "":
        raise HTTPException(status_code = 422, detail = "next_node cannot be empty.")
    if body.next_node.isnumeric():
        raise HTTPException(status_code = 422, detail = "next_node cannot be numbers only.")
    if body.thread_id == "":
        raise HTTPException(status_code = 422, detail = "thread_id cannot be empty.")
    if body.thread_id.isnumeric():
        raise HTTPException(status_code = 422, detail = "thread_id cannot be numbers.")
    try:
        response = code_review_service.resume_code_review(body.state_dictionary, body.next_node, body.thread_id)
        return response
    except TimeoutError as timeout_error:
        logger.error(f"Timeout in resume_code_review: {timeout_error}")
        raise HTTPException(status_code=504, detail="The request took too long to process. Please try again.")
    except Exception as _:
        error_detail = CustomException("Internal Server Error", error_details=sys.exc_info())
        logger.error(f"Error in resume_code_review: {error_detail}")
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.")
    
@app.get("/getworkflowimage", dependencies=[Depends(verify_api_key)])
@limiter.limit("10/minute")
def get_workflow_image(request: Request):
    root_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_directory = f"{root_directory}/images"
    image_path = os.path.join(save_directory, "AI_Augmented_SDLC_LangGraph_Workflow.png")
    if not os.path.exists(image_path):
        raise RuntimeError(f"File at path {image_path} does not exist.")
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    return Response(content=image_bytes, media_type="image/png")