# My Tools App
### Video Demo: https://youtu.be/USgkxFbrw94
#### A Web Application built using Python and Flask. 
#### Description: 
A Web Application built using Python and Flask. 
The home screen displays each tool or game to be explored by the user. The app is meant to
showcase small programs.

## Setup Instructions

### 1. Install Dependencies
```bash
python -m venv venv
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key
Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```
Get your API key from: https://platform.openai.com/api-keys



### 5. Start the Application
```bash
python main.py
```

## Troubleshooting


### "OpenAI API key not set" Error
Make sure you have:
1. Created a `.env` file in the root directory
2. Added your OpenAI API key: `OPENAI_API_KEY=your_key_here`
3. Obtained a valid API key from OpenAI

