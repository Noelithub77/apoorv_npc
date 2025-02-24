# LangChain Profile Manager

A Streamlit-based application that allows you to create and manage different conversation profiles using LangChain and Google's Generative AI.

## Features

- Create multiple conversation profiles with custom system prompts
- Add sample Q&A pairs for testing
- Test profiles with sample Q&A
- Interactive chat with loaded profiles
- Profile persistence in JSON format
- Easy profile import/export

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get a Google API key from Google AI Studio (https://makersuite.google.com/app/apikey)

3. Run the application:
```bash
streamlit run frontend.py
```

## Usage

1. Enter your Google API key in the sidebar
2. Create a new profile:
   - Enter profile name
   - Write system instructions
   - Add sample Q&A pairs
3. Load an existing profile
4. Test the profile:
   - Run sample Q&A tests
   - Use interactive chat

## Profile Format

Profiles are stored in `profiles.json` in the following format:

```json
[
  {
    "name": "Profile Name",
    "system_prompt": "System instructions...",
    "sample_qna": [
      {
        "question": "Sample question",
        "answer": "Expected answer"
      }
    ]
  }
]
``` 