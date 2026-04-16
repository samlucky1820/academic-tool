from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# Hugging Face API URL
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

# API KEY from Render environment variables
headers = {
    "Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"
}

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.json or {}
        text = data.get("text")

        if not text:
            return jsonify({"error": "No input text provided"}), 400

        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": text}
        )

        # Handle API errors properly
        if response.status_code != 200:
            return jsonify({
                "error": response.text,
                "status": response.status_code
            }), 500

        try:
            result = response.json()
        except Exception:
            return jsonify({
                "error": "Invalid JSON response from API",
                "raw": response.text
            }), 500

        # Extract output safely
        if isinstance(result, list) and len(result) > 0:
            return jsonify({
                "result": result[0].get("generated_text", "")
            })

        return jsonify({"result": str(result)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
