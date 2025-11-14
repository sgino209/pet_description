"""
Flask web application for Pet Description Utility
"""

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from pet_description import describe_pet, load_params
from PIL import Image
import io

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render the main page"""
    # Load default params from JSON
    default_params = load_params()
    return render_template('index.html', default_params=default_params)


@app.route('/api/describe', methods=['POST'])
def api_describe():
    """API endpoint to process pet image and return description"""
    try:
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Read image file
        image_data = file.read()
        
        # Validate image by trying to open it
        try:
            img = Image.open(io.BytesIO(image_data))
            img.verify()  # Verify it's a valid image
        except Exception as e:
            return jsonify({'success': False, 'error': f'Invalid image file: {str(e)}'}), 400
        
        # Reset file pointer
        img = Image.open(io.BytesIO(image_data))
        
        # Get parameters from form
        params = {
            'llm_engine': request.form.get('llm_engine', 'llava'),
            'language': request.form.get('language', 'english'),
            'temperature': float(request.form.get('temperature', 0.7)),
            'max_tokens': int(request.form.get('max_tokens', 512)),
            'ollama_base_url': request.form.get('ollama_base_url', 'http://localhost:11434')
        }
        
        # Add custom prompt if provided
        custom_prompt = request.form.get('prompt', '').strip()
        if custom_prompt:
            params['prompt'] = custom_prompt
        
        # Call describe_pet function
        result = describe_pet(img, params)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

