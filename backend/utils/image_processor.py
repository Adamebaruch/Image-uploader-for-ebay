import cv2
import numpy as np
from PIL import Image
import os

def analyze_image(image_path):
    """Analyze image and detect if it contains a game cartridge, disc, or case"""
    try:
        # Check if OpenCV is available
        if 'cv2' not in globals():
            return {"item_type": "unknown", "confidence": 0.0}
            
        image = cv2.imread(image_path)
        if image is None:
            return {"item_type": "unknown", "confidence": 0.0}
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect circles (potential discs)
        circles = cv2.HoughCircles(
            gray, 
            cv2.HOUGH_GRADIENT, 
            dp=1.2, 
            minDist=100,
            param1=50,
            param2=30,
            minRadius=50,
            maxRadius=300
        )
        
        # If circles are found, it's likely a disc
        if circles is not None:
            return {"item_type": "disc", "confidence": 0.85}
            
        # Detect rectangular shapes (potential cartridges or cases)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        largest_area = 0
        largest_contour = None
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > largest_area:
                largest_area = area
                largest_contour = contour
                
        if largest_contour is not None:
            # Analyze shape of largest contour
            perimeter = cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, 0.02 * perimeter, True)
            
            if len(approx) == 4:  # Rectangle
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h
                
                # Cartridges typically have a distinct aspect ratio
                if 0.5 <= aspect_ratio <= 0.8:
                    return {"item_type": "cartridge", "confidence": 0.75}
                # Cases often have a different aspect ratio
                elif 0.8 <= aspect_ratio <= 1.2:
                    return {"item_type": "case", "confidence": 0.7}
        
        return {"item_type": "unknown", "confidence": 0.3}
    
    except Exception as e:
        print(f"Error during image analysis: {str(e)}")
        return {"item_type": "unknown", "confidence": 0.0}