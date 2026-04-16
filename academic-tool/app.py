from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Hugging Face API (FIXED FORMAT)
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

headers = {
    "Authorization": "Bearer YOUR_HF_TOKEN_HERE"
}

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.json
        text = data.get("text")

        if not text:
            return jsonify({"error": "No input text"}), 400

        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": text}
        )

        if response.status_code != 200:
            return jsonify({
                "error": response.text,
                "status": response.status_code
            }), 500

        result = response.json()

        if isinstance(result, list):
            return jsonify({"result": result[0].get("generated_text", "")})

        return jsonify({"result": str(result)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
