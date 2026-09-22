import os
import uuid
from langchain_core.messages import HumanMessage, SystemMessage
from app.backend.workflow.state import util_state

def create_and_write_file(folder_name: str, messages: list, ai_response, model_name):
    if os.getenv("ENABLE_DEBUG_LOGGING", "false").lower() != "true":
        return
    if util_state["uuid"] == "":
        util_state["uuid"] = str(uuid.uuid4());
    base_folder = "C:\code_review_agentic ai_application"
    subfolder_path = os.path.join(base_folder, "archive",util_state["uuid"], folder_name)
    os.makedirs(subfolder_path, exist_ok=True)
    file_path = os.path.join(subfolder_path, "file1")
    with open(file_path, "w", encoding="utf-8") as f:
        for msg in messages[-1:]:
            if isinstance(msg, HumanMessage) == True:
                role = "HumanMessage: "
            elif isinstance(msg, SystemMessage) == True:
                role = "SystemMessage: "
            else:
                role = "AIMessage: "
            f.write(role)
            f.write("\n")
            f.write(msg.content)
            f.write("\n")
            f.write("AIMessage: ")
            f.write("\n")
            f.write(ai_response.content)
            f.write("\n")
            f.write(f"Model name: {model_name}")
            f.write("\n")