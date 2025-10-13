from flask import Blueprint

ai = Blueprint('ai',__name__, template_folder='templates', static_folder='static')


from flask import render_template, request, jsonify
from .sagan_chat import generate_response


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