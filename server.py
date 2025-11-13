# server.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI
import os, base64, re, traceback, time

app = Flask(__name__)
CORS(app)

# Get OpenAI key from Render Environment Variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("❌ ERROR: OPENAI_API_KEY is missing on Render.")
    print("Add it in Render → Environment → Add Variable")
    raise SystemExit

client = OpenAI(api_key=OPENAI_API_KEY)

# ==========================================
# Serve frontend (app.html)
# ==========================================
@app.route("/")
def home():
    return send_file("app.html")


# ==========================================
# Analyze uploaded image
# ==========================================
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        time.sleep(3)  # small delay to prevent rate limit

        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["image"]
        image_bytes = file.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt = (
            "You are ReUSEAI. Analyze this item and return exactly 3 short reuse ideas "
            "in one line each. Format like:\n"
            "1. ...\n2. ...\n3. ...\n"
        )

        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": f"data:image/jpeg;base64,{image_b64}"}
                    ]
                }
            ],
            max_output_tokens=200
        )

        # Extract text cleanly
        text = getattr(response, "output_text", str(response))
        lines = re.split(r'\d+\.\s*', text)
        ideas = [ln.strip() for ln in lines if ln.strip()]

        ideas = ideas[:3]  # ensure 3 items

        return jsonify({"ideas": ideas})

    except Exception as e:
        print("\n--- ERROR START ---")
        traceback.print_exc()
        print("--- ERROR END ---\n")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
# server.py