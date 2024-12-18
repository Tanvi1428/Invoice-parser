from flask import Flask, render_template, request, jsonify
from models import model1, model2, model3, model4, model5, model6
import os
import requests
from werkzeug.utils import secure_filename
import redis
import json
from datetime import datetime
import uuid

def verify_tesseract():
    """Verify Tesseract installation and configuration"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"Tesseract version: {version}")
        
        # Test with a simple image
        test_text = pytesseract.get_languages()
        print(f"Available languages: {test_text}")
        
        print("Tesseract verification successful!")
        return True
    except Exception as e:
        print(f"Tesseract verification failed: {str(e)}")
        print("TESSDATA_PREFIX:", os.getenv('TESSDATA_PREFIX'))
        return False
    
    
app = Flask(__name__)

# Define the path to save uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Redis
redis_client = redis.Redis(
    host='localhost',  # Change to 'redis' if using Docker
    port=6379,
    db=0,
    decode_responses=True  # Automatically decode responses to strings
)

def save_to_database(image_path, model_name, result_data, process_id):
    """Save processing details to Redis"""
    timestamp = datetime.now().isoformat()
    
    data = {
        'process_id': process_id,
        'timestamp': timestamp,
        'image_path': image_path,
        'model_used': model_name,
        'result': result_data,
        'feedback': None
    }
    
    # Store in Redis using process_id as key
    redis_client.set(f'invoice:process:{process_id}', json.dumps(data))
    
    # Add to process list for easy retrieval
    redis_client.lpush('invoice:processes', process_id)
    
    return process_id

def update_feedback(process_id, feedback_status):
    """Update feedback in Redis for a specific process"""
    key = f'invoice:process:{process_id}'
    
    # Get existing data
    data = redis_client.get(key)
    if data:
        data = json.loads(data)
        data['feedback'] = feedback_status
        data['feedback_timestamp'] = datetime.now().isoformat()
        
        # Update in Redis
        redis_client.set(key, json.dumps(data))
        
        # Add to feedback statistics
        redis_client.hincrby('invoice:feedback:stats', feedback_status, 1)
        
        return True
    return False

def call_model_api(image_path, model_name):
    """Call the appropriate model and return results"""
    model_mapping = {
        "model1": model1,
        "model2": model2,
        "model3": model3,
        "model4": model4,
        "model5": model5,
        "model6": model6
    }
    
    if model_name in model_mapping:
        try:
            invoice_data = model_mapping[model_name].parse(image_path)
            return {'status': 'success', 'data': invoice_data}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    else:
        return {'status': 'error', 'message': 'Model not found'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        image = request.files['image']
        model = request.form['model']
        
        if image and model:
            # Generate unique process ID
            process_id = str(uuid.uuid4())
            
            # Save image
            filename = secure_filename(image.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            image.save(image_path)
            
            # Process image with selected model
            result = call_model_api(image_path, model)
            
            # Save to database
            save_to_database(image_path, model, result, process_id)
            
            # Return response with process_id
            return jsonify({
                'status': 'success',
                'process_id': process_id,
                'result': result
            })
        
        return jsonify({
            'status': 'error',
            'message': 'Missing image or model selection'
        }), 400
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.get_json()
        process_id = data.get('process_id')
        status = data.get('status')
        
        if not process_id or not status:
            return jsonify({
                'status': 'error',
                'message': 'Missing process_id or feedback status'
            }), 400
            
        if status not in ['happy', 'sad']:
            return jsonify({
                'status': 'error',
                'message': 'Invalid feedback status'
            }), 400
        
        # Update feedback in database
        if update_feedback(process_id, status):
            return jsonify({
                'status': 'success',
                'message': f'Feedback recorded: {status}'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Process ID not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Additional routes for analytics and management

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get processing and feedback statistics"""
    try:
        total_processes = redis_client.llen('invoice:processes')
        feedback_stats = redis_client.hgetall('invoice:feedback:stats')
        
        return jsonify({
            'status': 'success',
            'stats': {
                'total_processes': total_processes,
                'feedback_stats': feedback_stats
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/process/<process_id>', methods=['GET'])
def get_process_details(process_id):
    """Get details for a specific process"""
    try:
        data = redis_client.get(f'invoice:process:{process_id}')
        if data:
            return jsonify({
                'status': 'success',
                'data': json.loads(data)
            })
        return jsonify({
            'status': 'error',
            'message': 'Process not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)