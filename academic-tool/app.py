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

        if response.status_code != 200:
            return jsonify({
                "error": response.text,
                "status": response.status_code
            }), 500

        try:
            result = response.json()
        except Exception:
            return jsonify({
                "error": "Invalid JSON response",
                "raw": response.text
            }), 500

        if isinstance(result, list) and len(result) > 0:
            return jsonify({
                "result": result[0].get("generated_text", str(result))
            })

        return jsonify({"result": str(result)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
