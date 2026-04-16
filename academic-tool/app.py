from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

headers = {}
if HF_API_TOKEN:
    headers["Authorization"] = f"Bearer {HF_API_TOKEN}"

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

        result = response.json()

        # Extract response safely
        if isinstance(result, list):
            return jsonify({"result": result[0].get("generated_text", str(result))})

        return jsonify({"result": str(result)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
