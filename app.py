from flask import Flask, render_template, request, jsonify
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
import json

# Initialize Flask app
app = Flask(__name__)

# Load trained model
# IMPORTANT: Make sure the model file is in the same directory or provide the correct path.
model = load_model("cultural_site_model.h5")

# Load site info from JSON
with open("site_info.json", "r", encoding="utf-8") as f:
    site_info = json.load(f)

# Create class names list
class_names = list(site_info.keys())

# --- NEW: Define a confidence threshold ---
# You can adjust this value (0.0 to 1.0) based on your model's performance.
# 0.80 means the model must be at least 80% confident.
CONFIDENCE_THRESHOLD = 0.80

# Home route
@app.route("/")
def home():
    return render_template("index.html")

# Predict route (handles image upload)
@app.route("/predict", methods=["POST"])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"})
    
    file = request.files['file']
    # Ensure the 'static' folder exists for temporary files
    if not os.path.exists('static'):
        os.makedirs('static')
    img_path = os.path.join("static", "temp.jpg")
    file.save(img_path)
    
    # Preprocess image
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x /= 255.0
    
    # Predict
    predictions = model.predict(x)
    
    # --- MODIFIED LOGIC ---
    # Get the confidence score of the top prediction
    confidence = np.max(predictions)
    
    # Check if the confidence is above our threshold
    if confidence > CONFIDENCE_THRESHOLD:
        # If confident, get the class name
        predicted_index = np.argmax(predictions)
        pred_class = class_names[predicted_index]
        
        # Delete temp image after use
        os.remove(img_path)
        
        # Redirect to AR info page
        return render_template("ar.html", site_name=pred_class)
    else:
        # If not confident, it's an unknown site
        # Delete temp image after use
        os.remove(img_path)
        
        # Return a page indicating the site was not found
        return render_template("not_found.html")

# Route to serve site info
@app.route("/site/<site_name>")
def site_details(site_name):
    info = site_info.get(site_name, None)
    if info:
        return jsonify(info)
    else:
        return jsonify({"error": "Site info not found"})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)