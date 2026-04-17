from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

HF_API_URL = "https://api-inference.huggingface.co/models/distilgpt2"
HF_API_TOKEN = os.getenv('HF_API_TOKEN')

headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing text field"}), 400
        
        user_text = data['text']
        
        if not user_text.strip():
            return jsonify({"error": "Text cannot be empty"}), 400
        
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": user_text},
            timeout=30
        )
        
        if response.status_code != 200:
            return jsonify({"error": f"API error: {response.text}"}), response.status_code
        
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            generated = result[0].get('generated_text', '')
            if generated.startswith(user_text):
                generated = generated[len(user_text):].strip()
            return jsonify({"result": generated or "No text generated"})
        
        return jsonify({"result": str(result)})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
