from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import requests
from PIL import Image
import io

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ModuleNotFoundError:
    CV2_AVAILABLE = False

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Homepage Route (Prevents 404 Error)
@app.route('/')
def home():
    return '''
    <h1>Ebay AI Photo Lister</h1>
    <p>Welcome! Use the <code>/upload</code> endpoint to upload an image.</p>
    <p>Try sending an image via Postman or cURL.</p>
    '''

# Function to detect if the image contains a game cartridge or disc
def detect_disc_or_cartridge(image_path):
    if not CV2_AVAILABLE:
        return "Disc detection unavailable (cv2 not installed)"
    
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)
    if circles is not None:
        return "Disc detected"
    else:
        return "No disc detected"

# Function to recognize the product using alternative OCR (Tesseract not available)
def recognize_product(image_path):
    try:
        image = Image.open(image_path)
        text = image.filename  # Fallback: Use file name if OCR is unavailable
        return text.strip() if text else "Unknown Product"
    except Exception as e:
        return f"OCR failed: {str(e)}"

# Function to fetch eBay sold listings (Mocked without API for now)
def fetch_ebay_solds(product_name):
    # Mocked response for now (can integrate eBay scraping later)
    sold_listings = {
        "Pokemon Gold": {"title": "Pokemon Gold Game Boy - Complete in Box", "price": "$120", "category": "Video Games"},
        "Super Mario 64": {"title": "Super Mario 64 - Cartridge Only", "price": "$40", "category": "Nintendo 64"},
    }
    return sold_listings.get(product_name, {"title": product_name, "price": "Unknown", "category": "Unknown"})

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Recognize product
    product_name = recognize_product(file_path)
    
    # Detect if a disc or cartridge is present
    disc_status = detect_disc_or_cartridge(file_path)
    
    # Fetch eBay sold listings
    ebay_data = fetch_ebay_solds(product_name)
    
    return jsonify({
        "title": ebay_data['title'],
        "price": ebay_data['price'],
        "category": ebay_data['category'],
        "description": f"This is a {ebay_data['title']} in great condition!",
        "disc_status": disc_status
    })

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)