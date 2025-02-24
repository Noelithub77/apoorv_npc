import json
import os
from typing import Dict, List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory

load_dotenv()

def init_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    return ChatGoogleGenerativeAI(
        google_api_key=api_key,
        model="gemini-2.0-flash",
        temperature=0.7,
    )

def create_conversation_chain(llm, system_prompt: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    memory = ConversationBufferMemory(
        return_messages=True,
        memory_key="history"
    )
    
    def chain_invoke(input_dict):
        history = memory.load_memory_variables({})["history"]
        messages = prompt.format_messages(history=history, input=input_dict["input"])
        response = llm.invoke(messages)
        result = response.content
        memory.save_context({"input": input_dict["input"]}, {"output": result})
        return result
        
    chain = {"invoke": chain_invoke, "memory": memory}
    return chain

def save_profile(profile_name: str, system_prompt: str, sample_qna: List[Dict], filepath: str):
    profile = {
        "name": profile_name,
        "system_prompt": system_prompt,
        "sample_qna": sample_qna
    }
    try:
        with open(filepath, "r") as f:
            profiles = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        profiles = []
    
    profiles = [p for p in profiles if p["name"] != profile_name]
    profiles.append(profile)
    
    with open(filepath, "w") as f:
        json.dump(profiles, f, indent=2)

def load_profiles(filepath: str) -> List[Dict]:
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def execute_sample_qna(chain, sample_qna: List[Dict]):
    responses = []
    for qa in sample_qna:
        response = chain["invoke"]({"input": qa["question"]})
        responses.append({
            "question": qa["question"],
            "expected": qa["answer"],
            "generated": response
        })
    return responses 