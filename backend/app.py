from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from assistant import SupermarketAssistant

app = Flask(__name__)
CORS(app)

assistant = SupermarketAssistant()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
        
    session_id = data.get('session_id', 'default')
    preferred_lang = data.get('preferred_lang', 'auto')
    
    response = assistant.process_message(data['message'], session_id, preferred_lang)
    return jsonify(response)

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    return jsonify({
        'count': len(assistant.inventory)
    })

if __name__ == '__main__':
    # Initialize from excel on startup
    try:
        assistant.load_inventory_from_excel('../inventory.xlsx')
        print(f"Loaded {len(assistant.inventory)} items from Excel.")
    except Exception as e:
        print(f"Warning: Could not load inventory from Excel: {e}")
        
    app.run(port=5000, debug=True)
