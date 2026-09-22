from dotenv import load_dotenv
import streamlit as st
st.markdown(
    """
    <style>
    header [data-testid="stAppDeployButton"] {display: none !important;}
    /* Robust: Make all sidebar buttons and their containers 100% width */
    section[data-testid="stSidebar"] button,
    section[data-testid="stSidebar"] [data-testid^="baseButton-button"] {
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        margin-bottom: 0.5rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
import html
import requests
import sys
import os
import uuid

load_dotenv()

# Configure page
st.set_page_config(page_title="AI Augmented SDLC Application", page_icon="🔍")

# Subprocess: Streamlit in the main.py file automatically switched the working directory to the "frontend" folder when launching the app.
# This prevented Python from seeing the utils package.
# Added the project's root directory to sys.path inside the Streamlit script. This ensured Python could locate the modules.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path: 
    sys.path.insert(0, ROOT_DIR)
from utils.bytes_converter import BytesConverter

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:9999");
INITIATE_CODE_REVIEW_API_URL = f"{API_BASE_URL}/initiatecodereview"
RESUME_CODE_REVIEW_API_URL = f"{API_BASE_URL}/resumecodereview"
HEADERS = {"x-api-key": os.getenv("API_KEY")}

# Role-based color mapping
role_colors = {
    "Human": "#2E86C1",
    "Business Analyst": "#1ABC9C",
    "Product Owner": "#AF7AC5",
    "System Designer": "#5DADE2",
    "Technical Architect": "#F39C12",
    "Software Developer 1": "#D35400",
    "Software Developer 2": "#CA6F1E",
    "Software Lead": "#884EA0",
    "Security Engineer": "#34495E",
    "QA Engineer": "#27AE60",
    "QA Reviewer": "#C0392B",
    "QA Lead": "#7D3C98"
}

# Initialize session state
default_states = {
    "api_key_submitted": False,
    "dictionary": [],
    "message_history": [],
    "pending_input": "",
    "waiting_for_response": False,
    "feedback_required_flag": False,
    "clear_input_flag": False,
    "last_stage": False
}
for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Assign a unique thread_id per user session
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = str(uuid.uuid4())

# Clear input when flagged
if st.session_state.clear_input_flag:
    st.session_state.user_input = ""
    st.session_state.clear_input_flag = False

# Hide sidebar with CSS if on workflow page
if st.session_state.get('page', 'chat') == 'workflow':
    st.markdown(
        """
        <style>
        section[data-testid='stSidebar'] {display: none !important;}
        </style>
        """,
        unsafe_allow_html=True
    )

# Only run sidebar code if not on workflow page
if st.session_state.get('page', 'chat') != 'workflow':
    st.sidebar.title("AI Augmented SDLC Control Panel")
    # In-app navigation: Workflow and About
    if 'page' not in st.session_state:
        st.session_state['page'] = 'chat'
    if st.sidebar.button("About"):
        st.session_state['about_visible'] = not st.session_state.get('about_visible', False)
    if 'about_visible' not in st.session_state:
        st.session_state['about_visible'] = False
    if st.session_state['about_visible']:
        st.sidebar.info("AI Augmented SDLC Demo App. Built with Streamlit, FastAPI, and LangGraph. Human-in-the-loop workflow for user story, code, design, and test automation.")
    if st.sidebar.button("SDLC Workflow Details"):
        st.session_state['page'] = 'workflow'
        st.rerun()

# Main App Title
st.markdown(
    '<h1 style="text-align:center; font-size:2.5rem; font-weight:bold; margin-bottom:1.5rem;">AI Augmented SDLC Application</h1>',
    unsafe_allow_html=True
)

# Show Workflow page if selected
if st.session_state['page'] == 'workflow':
    st.markdown('<h2 style="text-align:center;">AI Augmented SDLC Workflow</h2>', unsafe_allow_html=True)
    image_url = f"{API_BASE_URL}/getworkflowimage"
    try:
        # Try a quick connection to the backend
        requests.get(API_BASE_URL, timeout=2)
    except requests.exceptions.RequestException:
        st.error("❌ Cannot connect to the backend server. Please ensure the backend is running.")
    else:
        try:
            response = requests.get(image_url, headers=HEADERS)
            if response.status_code == 401:
                st.error("🔒 Unauthorized: Your API key is missing or invalid. Please check your credentials.")
            elif response.status_code == 403:
                st.error("🚫 Forbidden: You do not have permission to access this resource.")
            elif response.status_code == 429:
                st.error("⏳ Rate limit exceeded: Please wait a minute before trying again.")
            else:
                response.raise_for_status()
                st.image(response.content, caption="LangGraph Generated SDLC Workflow", width=700)
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Unable to load workflow image: {str(e)}")

    # --- Role Explanations Section ---
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<h3 style="text-align:center; margin-top:2em;">Workflow Nodes & Roles Explained</h3>', unsafe_allow_html=True)

    # Node/role mapping from state.py
    roles_dictionary = {
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

    # Node descriptions based on prompt_library.py
    node_descriptions = {
        "generate_user_stories": "Translates user input into actionable user stories, capturing goals and benefits.",
        "product_owner_review": "Reviews user stories for clarity, completeness, and alignment with product vision.",
        "human_loop_product_owner_review": "Allows a human to provide feedback or approval on the user stories.",
        "decision_product_owner_review": "Makes a final decision to approve or reject user stories based on reviews.",
        "create_design_docs": "Creates a comprehensive design document covering architecture, data flow, and APIs.",
        "revise_user_stories": "Refines user stories based on design document feedback and technical constraints.",
        "design_review": "Evaluates the design for feasibility, completeness, and alignment with requirements.",
        "human_loop_design_review": "Allows a human to review and provide feedback on the design document.",
        "decision_design_review": "Makes a final decision to approve or reject the design based on all reviews.",
        "generate_code": "Implements the required functionality in code, following best practices and design.",
        "code_review": "Reviews the code for correctness, style, completeness, and alignment with requirements.",
        "human_loop_code_review": "Allows a human to review and provide feedback on the code.",
        "decision_code_review": "Makes a final decision to approve or reject the code based on all reviews.",
        "security_review": "Analyzes the code for security vulnerabilities and recommends improvements.",
        "fix_code_after_code_review": "Updates the code to address feedback from the code review stage.",
        "fix_code_after_security": "Updates the code to address security review recommendations.",
        "write_test_cases": "Creates test cases to validate the code's functionality and edge cases.",
        "test_cases_review": "Reviews the test cases for completeness, accuracy, and coverage.",
        "human_loop_test_cases_review": "Allows a human to review and provide feedback on the test cases.",
        "decision_test_cases_review": "Makes a final decision to approve or reject the test cases based on all reviews.",
        "fix_test_cases": "Refines and enhances test cases based on review feedback."
    }

    st.markdown("""
    <div style='margin: 0 auto; max-width: 750px;'>
    <ul style='list-style: none; padding: 0;'>
    """, unsafe_allow_html=True)
    for node, role in roles_dictionary.items():
        if node == "messages":
            continue
        desc = node_descriptions.get(node, "No description available.")
        st.markdown(f"""
        <li style='margin-bottom: 1.2em; background: #f6f8fa; border-radius: 8px; padding: 1em 1.5em; box-shadow: 0 1px 4px rgba(0,0,0,0.04);'>
            <span style='color: #16896a; font-weight: bold; font-size: 1.1em;'>{role}</span>
            <span style='color: #888; font-size: 0.95em;'> ({node.replace('_', ' ').title()})</span><br>
            <span style='color: #333;'>{desc}</span>
        </li>
        """, unsafe_allow_html=True)
    st.markdown("</ul></div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.button("Back to Chat", on_click=lambda: st.session_state.update({'page': 'chat'}))
    st.stop()

# Chat history display
chat_html = """<div style="height:300px; overflow-y:auto; border:1px solid #ccc; padding:10px; background-color:#f9f9f9;">"""
if not st.session_state.message_history:
    chat_html += """<div style="text-align:center; color:gray; font-style:italic; margin-top: 100px;">Input is needed</div>"""
else:
    import re
    for msg in st.session_state.message_history:
        role = msg["role"]
        color = role_colors.get(role, "#000000")
        content = msg["content"]
        # Remove headings
        content = re.sub(r"^#+\\s*", "", content, flags=re.MULTILINE)
        # Remove bullet points
        content = re.sub(r"^[-*]\\s*", "", content, flags=re.MULTILINE)
        # Remove numbered lists
        content = re.sub(r"^\\d+\\.\\s*", "", content, flags=re.MULTILINE)
        # Remove bold/italic
        content = re.sub(r"(\*\*|__)(.*?)\1", r"\2", content)
        content = re.sub(r"(\*|_)(.*?)\1", r"\2", content)
        # Remove inline code
        content = re.sub(r"`([^`]*)`", r"\1", content)
        # Remove code blocks
        content = re.sub(r"```[\s\S]*?```", "", content)
        # Remove links
        content = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", content)
        content = html.escape(content)
        chat_html += f"""<div style="margin-bottom: 15px;">
                            <span style="color: {color}; font-weight: bold;">{role}:</span>
                            <pre style="color: {color}; white-space: pre-wrap; margin: 5px 0 0;">{content}</pre>
                            </div>"""
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# Human input required notification
if st.session_state.feedback_required_flag and not st.session_state.waiting_for_response:
    st.markdown(
        """<div style="background-color:#fff3cd; padding:10px; border-left:5px solid #f1c40f;
        border-radius:5px; margin-bottom:10px;">
            <strong>Review Required:</strong> Please read the responses from the team roles above
        and share your feedback or decision below.
        </div>""",
        unsafe_allow_html=True
    )

# Input form
input_placeholder = "Create a tic tac toe game." if not st.session_state.message_history else "Please provide input"
if st.session_state.last_stage:
    if st.session_state.last_stage:
        st.markdown(
            """<div style="background-color:#e8f6f3; padding:15px; border-left:5px solid #1abc9c;
            border-radius:5px; margin-bottom:20px;">
            ✅ <strong>SDLC life cycle is complete.</strong><br>
            Please press <em>Download</em> if you would like to save the results.
            </div>""",
            unsafe_allow_html=True
        )
        sdlc_life_cycle_text_bytes = BytesConverter.convert_to_text_bytes(st.session_state.dictionary[1]).encode("utf-8")
        st.download_button(
            "Download SDLC Life Cycle file",
            sdlc_life_cycle_text_bytes,
            "sdlc_life_cycle.txt",
            "text/plain"
        )
else:
    with st.form("input_form"):
        input_buffer = st.session_state.pending_input if st.session_state.waiting_for_response else ""
        input_text = st.text_input(
            label="Please provide input",
            value=input_buffer,
            key="user_input",
            disabled=st.session_state.waiting_for_response,
            placeholder=input_placeholder
        )
        submitted = st.form_submit_button("Send")
        if submitted and input_text:
            st.session_state.pending_input = input_text
            st.session_state.waiting_for_response = True
            st.rerun()

# Generate response
if st.session_state.waiting_for_response and st.session_state.pending_input:
    loading_placeholder = st.empty()
    loading_placeholder.markdown("**⏳ Processing your request... This may take 5-10 minutes for the workflow completion.**")

    input_text = st.session_state.pending_input
    role = st.session_state.dictionary[1][-1][0] if st.session_state.message_history else None

    try:
        if not st.session_state.message_history:
            payload = {'human_message': input_text, 'next_node': "generate_user_stories", 'thread_id': st.session_state['thread_id']}
            response = requests.post(INITIATE_CODE_REVIEW_API_URL, json=payload, timeout=900, headers=HEADERS)
            response.raise_for_status()
            st.session_state.dictionary = response.json()
        elif role == "Product Owner":
            st.session_state.dictionary[0]['human_loop_product_owner_review'] = input_text
            payload = {'state_dictionary': st.session_state.dictionary[0], 'next_node': "human_loop_product_owner_review", 'thread_id': st.session_state['thread_id']}
            response = requests.post(RESUME_CODE_REVIEW_API_URL, json=payload, timeout=900, headers=HEADERS)
            response.raise_for_status()
            st.session_state.dictionary = response.json()
        elif role == "Technical Architect":
            st.session_state.dictionary[0]['human_loop_design_review'] = input_text
            payload = {'state_dictionary': st.session_state.dictionary[0], 'next_node': "human_loop_design_review", 'thread_id': st.session_state['thread_id']}
            response = requests.post(RESUME_CODE_REVIEW_API_URL, json=payload, timeout=900, headers=HEADERS)
            response.raise_for_status()
            st.session_state.dictionary = response.json()
        elif role == "Software Developer 2":
            st.session_state.dictionary[0]['human_loop_code_review'] = input_text
            payload = {'state_dictionary': st.session_state.dictionary[0], 'next_node': "human_loop_code_review", 'thread_id': st.session_state['thread_id']}
            response = requests.post(RESUME_CODE_REVIEW_API_URL, json=payload, timeout=900, headers=HEADERS)
            response.raise_for_status()
            st.session_state.dictionary = response.json()
        elif role == "QA Reviewer":
            st.session_state.dictionary[0]['human_loop_test_cases_review'] = input_text
            payload = {'state_dictionary': st.session_state.dictionary[0], 'next_node': "human_loop_test_cases_review", 'thread_id': st.session_state['thread_id']}
            response = requests.post(RESUME_CODE_REVIEW_API_URL, json=payload, timeout=900, headers=HEADERS)
            response.raise_for_status()
            st.session_state.dictionary = response.json()
            last_role_list = st.session_state.dictionary[1][-1][0]
            if last_role_list is not None and last_role_list == "QA Engineer":
                st.session_state.last_stage = True
    except requests.exceptions.ConnectionError:
        loading_placeholder.empty()
        st.error("❌ Cannot connect to the backend server. Please ensure it's running.")
        st.session_state.waiting_for_response = False
        st.stop()
    except requests.exceptions.Timeout:
        loading_placeholder.empty()
        st.error("⏱️ Request timed out. Please try again.")
        st.session_state.waiting_for_response = False
        st.stop()
    except requests.exceptions.HTTPError as e:
        loading_placeholder.empty()
        try:
            error_msg = response.json().get('detail', 'Unknown error')
        except:
            error_msg = str(e)
        st.error(f"❌ Server error: {error_msg}")
        st.session_state.waiting_for_response = False
        st.stop()
    except Exception as e:
        loading_placeholder.empty()
        st.error(f"❌ Unexpected error: {str(e)}")
        st.session_state.waiting_for_response = False
        st.stop()

    # Reset message history
    st.session_state.message_history = [
        {"role": key, "content": value}
        for key, value in st.session_state.dictionary[1]
        if key != "messages"
    ]

    # Clear input on next run, hide loading, reenable input
    st.session_state.clear_input_flag = True
    st.session_state.pending_input = ""
    st.session_state.waiting_for_response = False
    st.session_state.feedback_required_flag = True
    if st.session_state.last_stage:
        st.session_state.feedback_required_flag = False
    loading_placeholder.empty()

    st.rerun()

# Inject CSS to make sidebar buttons and links look identical, with a less bright green
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] button, section[data-testid="stSidebar"] a.sdlc-btn {
        width: 100% !important;
        box-sizing: border-box;
        padding: 0.75em 1.2em;
        font-weight: bold;
        border-radius: 4px;
        margin-bottom: 0.5em;
        background: #16896a;
        color: white !important;
        text-decoration: none;
        text-align: center;
        display: block;
        border: none;
        transition: background 0.2s;
    }
    section[data-testid="stSidebar"] a.sdlc-btn:hover, section[data-testid="stSidebar"] button:hover {
        background: #11694f;
        color: white !important;
        text-decoration: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)