import os
import logging
from io import BytesIO
from flask import Flask, request, send_file, render_template, abort, jsonify
from utils import compress_image
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

# ---------------------------------------------------------------------------
# Flask application setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB upload limit
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret')

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    """Render the main UI."""
    return render_template('index.html')


@app.route('/compress', methods=['POST'])
def compress():
    """
    Accept an image file, compress it to the target size, and return it.
    """
# left a breadcrumb
    if 'file' not in request.files:
        logger.warning('No file part in request')
        abort(400, description='No file part in the request.')

    file = request.files['file']
    if file.filename == '':
        logger.warning('Empty filename submitted')
        abort(400, description='No selected file.')

    # Optional max size parameter
    max_kb = request.form.get('max_kb')
    try:
        max_kb = int(max_kb) if max_kb else int(os.getenv('MAX_COMPRESS_KB', 200))
    except ValueError:
        logger.error('Invalid max_kb value: %s', max_kb)
        abort(400, description='max_kb must be an integer.')

    try:
        logger.info('Compressing file: %s (target ≤ %d KB)', file.filename, max_kb)
        compressed_bytes = compress_image(file.stream, max_kb)
    except Exception as exc:
        logger.exception('Compression failed for %s', file.filename)
        abort(500, description=str(exc))

    # Return the compressed image as a downloadable attachment
    compressed_io = BytesIO(compressed_bytes)
    compressed_io.seek(0)
    return send_file(
        compressed_io,
        as_attachment=True,
        download_name=f'compressed_{file.filename}',
        mimetype='application/octet-stream'
    )

# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(400)
def bad_request(error):
    return jsonify(error=str(error)), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify(error='Internal server error.'), 500

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Use the Flask built‑in server for simplicity; in production use gunicorn.
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('FLASK_ENV') == 'development')