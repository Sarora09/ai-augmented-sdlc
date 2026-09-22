from dotenv import load_dotenv
from app.frontend import *
from app.exception.custom_exception import CustomException
from app.utils.logger import logger

import subprocess
import threading
import time
import sys

load_dotenv()

def run_backend():
    try:
        subprocess.run(["uvicorn", "app.backend.code_review_api:app", "--host", "localhost", "--port", "9999"], check=True)
    except Exception as _:
        raise
    
def run_frontend():
    try:
        subprocess.run(["streamlit", "run", "app/frontend/index.py"], check=True)
    except Exception as _:
        raise
    
if __name__ == "__main__":
    try:
        threading.Thread(target = run_backend).start()
        time.sleep(2)
        run_frontend()
    except Exception as e:
        error_detail = CustomException("Internal Server Error", error_details=sys.exc_info())
        logger.error(f"Error in main: {error_detail}")