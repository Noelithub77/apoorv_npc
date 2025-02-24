import json
import os
from typing import Dict, List, Callable
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from google.generativeai.types import HarmCategory, HarmBlockThreshold

load_dotenv()

def init_llm(streaming=False):
    api_key = os.getenv("GOOGLE_API_KEY")
    return ChatGoogleGenerativeAI(
        google_api_key=api_key,
        model="gemini-2.0-flash",
        temperature=0,
        streaming=streaming,
        safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH
        }
    )

def create_conversation_chain(llm, system_prompt: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("system", "{formatted_examples}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    memory = ConversationBufferMemory(
        return_messages=True,
        memory_key="history"
    )
    
    def chain_invoke(input_dict, streaming_callback=None):
        formatted_examples = ""
        if "sample_qna" in input_dict:
            formatted_examples = "You must follow these example interactions precisely. These examples define exactly how you should respond:\n\n"
            for i, qa in enumerate(input_dict["sample_qna"]):
                formatted_examples += f"Example {i+1}:\nUser: {qa['question']}\nYou: {qa['answer']}\n\n"
            formatted_examples += "Always maintain the same tone, style, and approach as shown in these examples."
        
        history = memory.load_memory_variables({})["history"]
        messages = prompt.format_messages(formatted_examples=formatted_examples, history=history, input=input_dict["input"])
        
        if streaming_callback:
            response_tokens = []
            for chunk in llm.stream(messages):
                token = chunk.content
                response_tokens.append(token)
                if streaming_callback:
                    streaming_callback(token)
            result = "".join(response_tokens)
        else:
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