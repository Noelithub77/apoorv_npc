import streamlit as st
import json
from langchain_app import (
    init_llm,
    create_conversation_chain,
    save_profile,
    load_profiles,
)

PROFILES_FILE = "profiles.json"

def init_session_state():
    if "profiles" not in st.session_state:
        st.session_state.profiles = load_profiles(PROFILES_FILE)
    if "current_profile" not in st.session_state:
        st.session_state.current_profile = None
    if "chain" not in st.session_state:
        st.session_state.chain = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "streaming_response" not in st.session_state:
        st.session_state.streaming_response = ""
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
    if "new_profile" not in st.session_state:
        st.session_state.new_profile = False
    if "llm" not in st.session_state:
        try:
            st.session_state.llm = init_llm(streaming=True)
        except ValueError as e:
            st.error(str(e))
            st.stop()

def toggle_edit_mode():
    st.session_state.edit_mode = not st.session_state.edit_mode
    
def create_new_profile():
    st.session_state.new_profile = True
    st.session_state.edit_mode = True
    st.session_state.current_profile = {
        "name": "",
        "system_prompt": "",
        "sample_qna": [{"question": "", "answer": ""}]
    }

def get_profiles_data():
    with open(PROFILES_FILE, "r") as f:
        return f.read()

def main():
    st.title("Enigma x GDU Apoorv Game")
    init_session_state()

    st.sidebar.download_button(
        label="Download json",
        data=get_profiles_data(),
        file_name=PROFILES_FILE,
        mime="application/json"
    )
    st.sidebar.header("Character Selection")
    profile_names = [p["name"] for p in st.session_state.profiles]
    
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        selected_profile = st.selectbox(
            "Select Character", 
            profile_names,
            key="profile_selector"
        )
    with col2:
        if st.button("➕", help="Add new profile"):
            create_new_profile()
    
    
    if selected_profile and not st.session_state.new_profile:
        profile = next(p for p in st.session_state.profiles if p["name"] == selected_profile)
        st.session_state.current_profile = profile
        st.session_state.chain = create_conversation_chain(
            st.session_state.llm,
            profile["system_prompt"]
        )

    if st.session_state.current_profile:
        if not st.session_state.edit_mode:
            st.sidebar.button("Edit", on_click=toggle_edit_mode)
            
            st.header("Test Character")
            
            for role, message in st.session_state.chat_history:
                with st.chat_message(role):
                    st.write(message)
            
            if "response_placeholder" not in st.session_state:
                st.session_state.response_placeholder = st.empty()
            
            user_input = st.chat_input("Your message")
            if user_input:
                st.session_state.chat_history.append(("Human", user_input))
                
                with st.chat_message("Human"):
                    st.write(user_input)
                
                with st.chat_message("Assistant"):
                    message_placeholder = st.empty()
                    st.session_state.streaming_response = ""
                    
                    def on_token(token):
                        st.session_state.streaming_response += token
                        message_placeholder.write(st.session_state.streaming_response)
                    
                    full_response = st.session_state.chain["invoke"](
                        {
                            "input": user_input,
                            "sample_qna": st.session_state.current_profile["sample_qna"]
                        },
                        streaming_callback=on_token
                    )
                    
                    st.session_state.chat_history.append(("Assistant", full_response))
        else:
            st.sidebar.button("Back to Chat", on_click=toggle_edit_mode)
            
            st.header("Edit Character")
            
            if "name" not in st.session_state.current_profile:
                st.session_state.current_profile["name"] = ""
            if "system_prompt" not in st.session_state.current_profile:
                st.session_state.current_profile["system_prompt"] = ""
            if "sample_qna" not in st.session_state.current_profile:
                st.session_state.current_profile["sample_qna"] = [{"question": "", "answer": ""}]
                
            profile_name = st.text_input(
                "Profile Name", 
                value=st.session_state.current_profile["name"]
            )
            
            system_prompt = st.text_area(
                "System Instructions", 
                value=st.session_state.current_profile["system_prompt"]
            )

            st.subheader("Sample Q&A Pairs")
            
            current_qna = st.session_state.current_profile["sample_qna"]
            if not current_qna:  
                current_qna = [{"question": "", "answer": ""}]
                
            num_pairs = st.number_input("Number of Q&A Pairs", min_value=0, value=len(current_qna))
            
            sample_qna = []
            for i in range(num_pairs):
                col1, col2 = st.columns(2)
                with col1:
                    question = st.text_input(
                        f"Question {i+1}", 
                        value=current_qna[i]["question"] if i < len(current_qna) else ""
                    )
                with col2:
                    answer = st.text_input(
                        f"Expected Answer {i+1}", 
                        value=current_qna[i]["answer"] if i < len(current_qna) else ""
                    )
                sample_qna.append({"question": question, "answer": answer})

            if st.button("Save Profile"):
                profile_name = profile_name or f"Character {len(st.session_state.profiles) + 1}"
                system_prompt = system_prompt or ""
                
                save_profile(profile_name, system_prompt, sample_qna, PROFILES_FILE)
                st.session_state.profiles = load_profiles(PROFILES_FILE)
                
                st.session_state.current_profile = next(
                    (p for p in st.session_state.profiles if p["name"] == profile_name), 
                    None
                )
                
                if st.session_state.current_profile:
                    st.session_state.chain = create_conversation_chain(
                        st.session_state.llm,
                        st.session_state.current_profile["system_prompt"]
                    )
                
                st.session_state.new_profile = False
                st.session_state.edit_mode = False
                st.success(f"Profile '{profile_name}' saved successfully!")
                st.rerun()

if __name__ == "__main__":
    main() 