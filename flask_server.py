from flask import Flask, request, jsonify
from langchain_app import init_llm, create_conversation_chain, load_profiles
import os

app = Flask(__name__)


llm = init_llm(streaming=False)
PROFILES_FILE = "profiles.json"


profile_chains = {}

def get_chain_for_profile(profile_name):
    if profile_name not in profile_chains:
        profiles = load_profiles(PROFILES_FILE)
        profile = next((p for p in profiles if p["name"] == profile_name), None)
        if not profile:
            return None
        profile_chains[profile_name] = create_conversation_chain(llm, profile["system_prompt"])
    return profile_chains[profile_name]

@app.route("/characters", methods=["GET"])
def list_characters():
    profiles = load_profiles(PROFILES_FILE)
    return jsonify([p["name"] for p in profiles])

@app.route("/chat/<character_name>", methods=["POST"])
def chat_with_character(character_name):
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400
    
    chain = get_chain_for_profile(character_name)
    if not chain:
        return jsonify({"error": f"Character '{character_name}' not found"}), 404
    
    profiles = load_profiles(PROFILES_FILE)
    profile = next((p for p in profiles if p["name"] == character_name), None)
    
    response = chain["invoke"]({
        "input": data["message"],
        "sample_qna": profile["sample_qna"]
    })
    
    return jsonify({
        "character": character_name,
        "message": data["message"],
        "response": response
    })

@app.route("/reset/<character_name>", methods=["POST"])
def reset_character(character_name):
    if character_name in profile_chains:
        del profile_chains[character_name]
        return jsonify({"message": f"Conversation reset for character '{character_name}'"})
    return jsonify({"error": f"Character '{character_name}' not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000) 