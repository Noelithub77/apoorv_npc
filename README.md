# API docs:-

flask runs on `http://localhost:5000` and provides the following endpoints:

### 1. List Characters
```http
GET /characters
```
Returns a list of all available character names. Just to test if the server is on actually

**Response Example:**
```json
["Victor paul", "Baliga"]
```

### 2. Chat with Character
```http
POST /chat/<character_name>
```
Send a message to a specific character and get their response.

**Request Body:**
```json
{
    "message": "Hello"
}
```

**Response Example:**
```json
{
    "character": "Victor paul",
    "message": "Hello",
    "response": "Hello, how are you?"
}
```

### 3. Reset Character Conversation
```http
POST /reset/<character_name>
```
Resets the conversation history for a specific character.

**Response Example:**
```json
{
    "message": "Conversation reset for character 'Detective Smith'"
}
```

# Setup and Running:-

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with:
```
GOOGLE_API_KEY=your_api_key_here
```

3. Run the application:
```bash
streamlit run frontend.py
```

This will start both the Streamlit UI and the Flask API server.

## Using the API

Example using curl:

```bash
# List all characters
curl http://localhost:5000/characters

# Chat with a character
curl -X POST http://localhost:5000/chat/victor%20paul \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Reset a character's conversation
curl -X POST http://localhost:5000/reset/victor%20paul
```


