import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for your frontend

# API Keys from environment variables
API_KEYS = [
    os.getenv('OPENROUTER_KEY_1'),
    os.getenv('OPENROUTER_KEY_2'),
    os.getenv('OPENROUTER_KEY_3'),
]

# Remove None values (in case you don't set all keys)
API_KEYS = [key for key in API_KEYS if key]

current_key_index = 0

@app.route('/api/analyze-trade', methods=['POST'])
def analyze_trade():
    global current_key_index
    
    try:
        data = request.json
        prompt = data.get('prompt')
        
        # Validation
        if not prompt or not isinstance(prompt, str):
            return jsonify({"error": "Invalid prompt"}), 400
        
        if len(prompt) > 50000:
            return jsonify({"error": "Prompt too long"}), 400
        
        # Try each API key
        for attempt in range(len(API_KEYS)):
            api_key = API_KEYS[current_key_index]
            
            print(f"Attempting with key {current_key_index + 1}/{len(API_KEYS)}")
            
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "openai/gpt-oss-20b:free",
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=30
                )
                
                # Rate limited - try next key
                if response.status_code == 429:
                    print(f"Key {current_key_index + 1} rate limited (429)")
                    current_key_index = (current_key_index + 1) % len(API_KEYS)
                    continue
                
                # Other error - return immediately
                if response.status_code != 200:
                    return jsonify({
                        "error": f"OpenRouter API error: {response.status_code}",
                        "details": response.text
                    }), response.status_code
                
                # Success!
                print(f"Success with key {current_key_index + 1}")
                return jsonify(response.json()), 200
                
            except requests.exceptions.RequestException as e:
                print(f"Request error with key {current_key_index + 1}: {e}")
                current_key_index = (current_key_index + 1) % len(API_KEYS)
                continue
        
        # All keys exhausted
        return jsonify({
            "error": "ALL_KEYS_RATE_LIMITED",
            "message": "We have exhausted all available API limits from our provider. Please try again later."
        }), 429
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Your existing routes...
# @app.route('/api/items', methods=['GET'])
# def get_items():
#     ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
