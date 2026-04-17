from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# IMPORTANT: Use the FULL URL, not just /models/distilgpt2
HF_API_URL = "https://api-inference.huggingface.co/models/distilgpt2"

# Get your token from environment variable
HF_API_TOKEN = os.getenv('HF_API_TOKEN')

# Check if token exists
if not HF_API_TOKEN:
    print("ERROR: HF_API_TOKEN environment variable not set!")
    print("Please run: export HF_API_TOKEN='your_token_here'")
    print("Get token from: https://huggingface.co/settings/tokens")

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        user_text = data.get('text', '')
        
        if not user_text:
            return jsonify({"error": "Please enter some text"}), 400
        
        print(f"Sending to Hugging Face: {user_text}")
        print(f"URL: {HF_API_URL}")
        print(f"Headers: Authorization: Bearer {HF_API_TOKEN[:10]}...")
        
        # Make the request to Hugging Face
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": user_text},
            timeout=60
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated = result[0].get('generated_text', '')
                # Remove the input text if it's included
                if generated.startswith(user_text):
                    generated = generated[len(user_text):]
                return jsonify({"result": generated.strip()})
            return jsonify({"result": str(result)})
        else:
            return jsonify({
                "error": f"Hugging Face API returned {response.status_code}: {response.text[:200]}"
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting server on port {port}")
    print(f"Using Hugging Face API: {HF_API_URL}")
    app.run(host="0.0.0.0", port=port, debug=True)
