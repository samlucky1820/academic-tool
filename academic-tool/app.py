from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# ✅ Hugging Face Inference API (stable endpoint)
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

# ✅ API key from Render Environment Variables
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

        # Call Hugging Face API
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": text}
        )

        # If Hugging Face returns error
        if response.status_code != 200:
            return jsonify({
                "error": response.text,
                "status": response.status_code
            }), 500

        # Parse response safely
        try:
            result = response.json()
        except Exception:
            return jsonify({
                "error": "Invalid JSON response from API",
                "raw": response.text
            }), 500

        # Extract generated text
        if isinstance(result, list) and len(result) > 0:
            return jsonify({
                "result": result[0].get("generated_text", "")
            })

        return jsonify({"result": str(result)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Required for Render (VERY IMPORTANT)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
