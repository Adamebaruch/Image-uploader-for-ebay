from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import logging
import uuid
from PIL import Image
import io

# Import utility modules
from utils.image_processor import analyze_image
from utils.ebay_connector import identify_product, get_product_details

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return '''
    <h1>eBay AI Photo Lister API</h1>
    <p>Upload an image to <code>/api/analyze</code> to get eBay listing suggestions.</p>
    <p>For more information, see the documentation.</p>
    '''

@app.route('/api/analyze', methods=['POST'])
def analyze_uploaded_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({
            "error": "File type not allowed", 
            "allowed_types": list(app.config['ALLOWED_EXTENSIONS'])
        }), 400

    # Create unique filename
    filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        file.save(file_path)
        logger.info(f"Saved uploaded file to {file_path}")
        
        # Analyze image
        image_analysis = analyze_image(file_path)
        item_type = image_analysis["item_type"]
        
        # Try to identify product from filename
        product_id = identify_product(file.filename)
        
        # No product identified
        if not product_id:
            return jsonify({
                "success": False,
                "message": "Could not identify product in image",
                "analysis": {
                    "item_type": item_type,
                    "confidence": image_analysis["confidence"]
                }
            }), 200
        
        # Get product details
        product_details = get_product_details(product_id, item_type)
        
        if not product_details:
            return jsonify({
                "success": False,
                "message": "Product identified but details not found",
                "product_id": product_id
            }), 200
            
        # Get default pricing (first option)
        price = product_details["pricing"][0]["price"] if product_details["pricing"] else 0
        
        # Prepare response
        response = {
            "success": True,
            "product_id": product_id,
            "title": product_details["title"],
            "category": product_details["category"],
            "description": product_details["description"],
            "item_type": item_type,
            "confidence": image_analysis["confidence"],
            "pricing_options": product_details["pricing"],
            "ebay_listing": {
                "title": f"{product_details['title']} - {item_type.title()}",
                "category": product_details["category"],
                "price": price,
                "description": product_details["description"],
                "condition": "Used" 
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    logger.info("Starting eBay AI Photo Lister server")
    app.run(debug=True, host='0.0.0.0', port=5000)