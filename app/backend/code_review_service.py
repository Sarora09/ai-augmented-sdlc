import os
from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig
from app.backend.workflow.graph_builder import build_graph
from app.backend.workflow.state import util_state, roles_dictionary

def construct_streamlit_message(full_state: dict):
    message_state = []
    for key, value in full_state.items():
        if key == "Human":
            message_state.append(("Human", value))
        else:
            mapped_key = roles_dictionary[key]
            message_state.append((mapped_key, value))
    return message_state

def initiate_code_review(input_message, next_node, thread_id):
    graph = build_graph();
    root_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_directory = f"{root_directory}/images"
    os.makedirs(save_directory, exist_ok=True)
    file_path = os.path.join(save_directory, "AI_Augmented_SDLC_LangGraph_Workflow.png")
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f: 
            f.write(graph.get_graph().draw_mermaid_png())
    util_state["initial_input"] = HumanMessage(content = input_message);
    thread = {
        "configurable": {
            "thread_id": thread_id,
            "next_node": next_node
            }
            }
    full_state = {"Human": util_state["initial_input"].content}
    config = RunnableConfig(recursion_limit=100, configurable=thread["configurable"])
    pre_hitl_state = "product_owner_review"
    for event in graph.stream({"messages": [util_state["initial_input"]]}, config=config, stream_mode="values"):
        full_state.update(event)
        previous_states = [k for k in event.keys() if k != "messages"]
        if len(previous_states) >= 1 and previous_states[-1] == pre_hitl_state:
            break
    streamlit_message = construct_streamlit_message(full_state)
    return [full_state, streamlit_message]
    
def resume_code_review(state, next_node, thread_id):
    graph = build_graph();
    thread = {
        "configurable": {
            "thread_id": thread_id,
            "next_node": next_node
            }
            }
    full_state = state.copy()
    pre_hitl_state = ""

    if next_node == "human_loop_product_owner_review":
        pre_hitl_state = "design_review"
    elif next_node == "human_loop_design_review":
        pre_hitl_state = "code_review"
    elif next_node == "human_loop_code_review":
        pre_hitl_state = "test_cases_review"
    elif next_node == "human_loop_test_cases_review":
        pre_hitl_state = ""

    pre_hitl_states = ["product_owner_review", "design_review", "code_review", "test_cases_review"]
    
    config = RunnableConfig(recursion_limit=100, configurable=thread["configurable"])
    current_node_name = ""
    trim_state = False
    for event in graph.stream(state, config=config, stream_mode="updates"):
        # print(event.keys())
        if 'router' in event.keys():
            continue
        single_node_list = [k for k in event.keys()]
        current_node_name = single_node_list[0]
        print("current_node_name Line 1: ", current_node_name)
        # print("event: ", event)
        current_key_value_pair = {current_node_name: event[current_node_name][current_node_name]}
        # print("current_key_value_pair: ",current_key_value_pair )
        full_state.update(current_key_value_pair)
        print("current_node_name Line 2: ", current_node_name)
        print("next_node Line 3: ", next_node)
        print("full_state[next_node] Line 4: ", full_state[next_node])
        # When human in loop response is Reject
        if current_node_name in pre_hitl_states and full_state[next_node] is not None:
            # print(full_state)
            trim_state = True
            break
        # When human in loop response is Approve
        if current_node_name == pre_hitl_state:
            # print(full_state)
            break
    if trim_state == True:
        result = {}
        for key in full_state:
            result[key] = full_state[key]
            if key == current_node_name:
                break
        streamlit_message = construct_streamlit_message(result)
        return [result, streamlit_message]
    streamlit_message = construct_streamlit_message(full_state)
    return [full_state, streamlit_message]