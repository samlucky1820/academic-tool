from flask import Flask, render_template, request, jsonify
import requests
import os
import json

app = Flask(__name__)

# Use the CORRECT Hugging Face API endpoint
API_URL = "https://api-inference.huggingface.co/models/distilgpt2"

# Your token (you've given permission)
headers = {
    "Authorization": "Bearer hf_YOUR_TOKEN_HERE",  # Replace with your actual token
    "Content-Type": "application/json"
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        # Get text from request
        data = request.get_json()
        user_input = data.get("text", "")
        
        if not user_input:
            return jsonify({"error": "Please enter some text"}), 400
        
        print(f"📝 Generating for: {user_input}")
        
        # Prepare the payload
        payload = {
            "inputs": user_input,
            "parameters": {
                "max_length": 100,
                "temperature": 0.7,
                "do_sample": True
            }
        }
        
        # Make request to Hugging Face
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"✅ API Response Status: {response.status_code}")
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            
            # Extract the generated text
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                
                # Remove the input text from the output if it's repeated
                if generated_text.startswith(user_input):
                    generated_text = generated_text[len(user_input):].strip()
                
                return jsonify({"result": generated_text})
            else:
                return jsonify({"result": str(result)})
        else:
            # Handle errors
            error_msg = f"API Error {response.status_code}: {response.text}"
            print(f"❌ {error_msg}")
            return jsonify({"error": error_msg}), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out. Please try again."}), 504
    except Exception as e:
        print(f"❌ Server Error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Server running on http://localhost:{port}")
    print(f"🔗 Using Hugging Face API: {API_URL}")
    app.run(host="0.0.0.0", port=port, debug=True)
