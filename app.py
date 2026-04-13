import os
import tempfile

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request, stream_with_context

from pdf_processor import get_relevant_chunks, process_pdf
from reviewer import create_review_stream, stream_review_response


load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_pdf():
    uploaded_file = request.files.get("file")

    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"success": False, "message": "No file uploaded."}), 400

    if not uploaded_file.filename.lower().endswith(".pdf"):
        return jsonify({"success": False, "message": "Please upload a PDF file."}), 400

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            uploaded_file.save(temp_file)
            temp_path = temp_file.name

        chunk_count = process_pdf(temp_path)
        return jsonify({"success": True, "chunk_count": chunk_count})
    except Exception as exc:
        return jsonify({"success": False, "message": f"PDF processing failed: {exc}"}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.route("/review", methods=["POST"])
def review_document():
    payload = request.get_json(silent=True) or {}
    query = (payload.get("query") or "").strip()

    if not query:
        return jsonify({"success": False, "message": "Query cannot be empty."}), 400

    try:
        chunks = get_relevant_chunks(query, k=3)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception as exc:
        return jsonify({"success": False, "message": f"Failed to retrieve document chunks: {exc}"}), 500

    if not chunks:
        return jsonify({"success": False, "message": "No relevant document chunks were found."}), 400

    try:
        review_stream = create_review_stream(query=query, chunks=chunks)
    except Exception as exc:
        return jsonify({"success": False, "message": f"Groq API error: {exc}"}), 500

    @stream_with_context
    def generate():
        yield from stream_review_response(review_stream)

    return Response(generate(), mimetype="text/plain; charset=utf-8")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
