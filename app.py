import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/get-keys', methods=['GET'])
def get_keys():
    """Return all available API keys"""
    keys = [
        os.getenv('OPENROUTER_KEY_1'),
        os.getenv('OPENROUTER_KEY_2'),
        os.getenv('OPENROUTER_KEY_3'),
        os.getenv('OPENROUTER_KEY_4')
    ]
    
    # Remove None values
    keys = [key for key in keys if key]
    
    if not keys:
        return jsonify({"error": "No API keys configured"}), 500
    
    return jsonify({"keys": keys}), 200

# Your other existing routes...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
