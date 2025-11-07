from flask import Flask, jsonify

app = Flask(__name__)

# In-memory sample data
SAMPLE_ITEMS = [
    {"id": 1, "name": "Alpha", "description": "Sample item A"},
    {"id": 2, "name": "Bravo", "description": "Sample item B"},
]


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/items", methods=["GET"])
def list_items():
    return jsonify({"items": SAMPLE_ITEMS}), 200


@app.errorhandler(500)
def handle_500(e):
    return jsonify({"error": "internal_server_error", "message": str(e)}), 500


if __name__ == "__main__":
    # Bind to localhost for development
    app.run(host="127.0.0.1", port=5000, debug=True)
