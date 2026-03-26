from flask import Flask, request, jsonify
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 DocuGlass AI Backend Running"

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Empty file"}), 400

        # 🔐 Secure credentials from environment
        endpoint = os.environ.get("AZURE_ENDPOINT")
        key = os.environ.get("AZURE_KEY")

        if not endpoint or not key:
            return jsonify({"error": "Azure credentials not set"}), 500

        client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )

        file_bytes = file.read()

        # 🚫 File size check (5MB limit)
        if len(file_bytes) > 5 * 1024 * 1024:
            return jsonify({"error": "File too large (max 5MB)"}), 400

        poller = client.begin_analyze_document("prebuilt-read", file_bytes)
        result = poller.result()

        full_text = ""
        for page in result.pages:
            for line in page.lines:
                full_text += line.content + "\n"

        return jsonify({"text": full_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Required for Vercel
def handler(request):
    return app(request)