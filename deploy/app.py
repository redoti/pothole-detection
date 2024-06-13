from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import numpy as np
import binascii

app = Flask(__name__)
CORS(app)  # Enable CORS

# Model Path
best_model_path = "model.pt"
best_model = YOLO(best_model_path)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if 'image_hex' not in data:
        return jsonify({'error': 'No hex image string provided'}), 400

    image_hex = data['image_hex']
    
    try:
        # Decode the hex string to bytes
        image_bytes = binascii.unhexlify(image_hex)
    except binascii.Error:
        return jsonify({'error': 'Invalid hex string'}), 400

    # Convert bytes to numpy array and then to image
    image_np = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    # Perform inference on the image
    results = best_model.predict(source=image, imgsz=640)
    annotated_image = results[0].plot()
    annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
    count_pothole = len(results[0])

    # Convert the annotated image to hex
    _, buffer = cv2.imencode('.jpg', annotated_image_rgb)
    hex_image = buffer.tobytes().hex()

    return jsonify({
        'count_pothole': count_pothole,
        'annotated_image_hex': hex_image
    })

if __name__ == '__main__':
    app.run(debug=True)