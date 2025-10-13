from flask import Blueprint
from flask import render_template, request, jsonify
from .sagan_chat import generate_response
import os
import requests

ai = Blueprint('ai',__name__, template_folder='templates', static_folder='static')

INDEX_PATH = os.path.join(os.path.dirname(__file__), "sagan_index.faiss")
GDRIVE_FILE_ID = "1n-Emm343C5NlkutYPfmsXymIdJZtpTP9"

def download_faiss_index():
    if not os.path.exists(INDEX_PATH):
        print("Downloading FAISS index...")
        url = f"https://drive.google.com/uc?export=download&id={GDRIVE_FILE_ID}"
        r = requests.get(url)
        with open(INDEX_PATH, 'wb') as f:
            f.write(r.content)
        print("Download complete.")

download_faiss_index()


@ai.route('/chat')
def chat():
    return render_template('sagan_chat.html')

@ai.route('/ask', methods=['POST'])
def ask_sagan():
    data = request.get_json()
    print("Request data:", data)  # Debugging line

    query = data.get('query', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    try:
        response = generate_response(query)
        print("Generated response:", response)  # Debugging line
        return jsonify({'response': response})
    except Exception as e:
        print("Error generating response:", e)  # Debugging line
        return jsonify({'error': str(e)}), 500