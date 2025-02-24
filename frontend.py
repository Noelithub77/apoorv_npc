import streamlit as st
import json
from langchain_app import (
    init_llm,
    create_conversation_chain,
    save_profile,
    load_profiles,
    execute_sample_qna
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
    if "llm" not in st.session_state:
        try:
            st.session_state.llm = init_llm(streaming=True)
        except ValueError as e:
            st.error(str(e))
            st.stop()

def main():
    st.title("Enigma x GDU Apoorv Game")
    init_session_state()

    st.sidebar.header("Model Selection")
    profile_names = [p["name"] for p in st.session_state.profiles]
    selected_profile = st.sidebar.selectbox("Select Character", profile_names)

    if selected_profile:
        profile = next(p for p in st.session_state.profiles if p["name"] == selected_profile)
        st.session_state.current_profile = profile
        st.session_state.chain = create_conversation_chain(
            st.session_state.llm,
            profile["system_prompt"]
        )

    st.header("Alter Characters:-")
    profile_name = st.text_input("Profile Name", value=st.session_state.current_profile["name"] if st.session_state.current_profile else "")
    system_prompt = st.text_area("System Instructions", value=st.session_state.current_profile["system_prompt"] if st.session_state.current_profile else "")

    st.subheader("Sample Q&A Pairs")
    num_pairs = st.number_input("Number of Q&A Pairs", min_value=1, value=len(st.session_state.current_profile["sample_qna"]) if st.session_state.current_profile else 1)
    sample_qna = []

    for i in range(num_pairs):
        col1, col2 = st.columns(2)
        with col1:
            question = st.text_input(f"Question {i+1}", value=st.session_state.current_profile["sample_qna"][i]["question"] if st.session_state.current_profile and i < len(st.session_state.current_profile["sample_qna"]) else "")
        with col2:
            answer = st.text_input(f"Expected Answer {i+1}", value=st.session_state.current_profile["sample_qna"][i]["answer"] if st.session_state.current_profile and i < len(st.session_state.current_profile["sample_qna"]) else "")
        if question and answer:
            sample_qna.append({"question": question, "answer": answer})

    if st.button("Save Profile") and profile_name and system_prompt and sample_qna:
        save_profile(profile_name, system_prompt, sample_qna, PROFILES_FILE)
        st.session_state.profiles = load_profiles(PROFILES_FILE)
        st.success(f"Profile '{profile_name}' saved successfully!")

    st.header("Test Character")
    if st.button("Run Sample Q&A"):
        with st.spinner("Testing..."):
            results = execute_sample_qna(
                st.session_state.chain,
                sample_qna
            )

        for i, result in enumerate(results, 1):
            st.subheader(f"Test Case {i}")
            st.write("Question:", result["question"])
            st.write("Expected:", result["expected"])
            st.write("Generated:", result["generated"])
            st.divider()

    st.subheader("Interactive Chat")
    
    # Display chat history
    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(message)
    
    # Create a placeholder for streaming responses
    if "response_placeholder" not in st.session_state:
        st.session_state.response_placeholder = st.empty()
    
    # Handle user input
    user_input = st.chat_input("Your message")
    if user_input and st.session_state.current_profile:
        # Add user message to chat history
        st.session_state.chat_history.append(("You", user_input))
        
        # Display user message
        with st.chat_message("You"):
            st.write(user_input)
        
        # Create a placeholder for the assistant's response
        with st.chat_message("Assistant"):
            message_placeholder = st.empty()
            st.session_state.streaming_response = ""
            
            # Define callback function for streaming
            def on_token(token):
                st.session_state.streaming_response += token
                message_placeholder.write(st.session_state.streaming_response)
            
            # Invoke the chain with streaming
            full_response = st.session_state.chain["invoke"](
                {
                    "input": user_input,
                    "sample_qna": st.session_state.current_profile["sample_qna"]
                },
                streaming_callback=on_token
            )
            
            # Add the complete response to chat history
            st.session_state.chat_history.append(("Assistant", full_response))

if __name__ == "__main__":
    main() 