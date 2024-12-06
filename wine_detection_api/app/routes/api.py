from flask import Blueprint, request, jsonify
from wine_detection_api.app.utils.detector import WineDetector
from wine_detection_api.config import Config
import cv2
import numpy as np


api = Blueprint('api', __name__)
detector = WineDetector(Config.MODEL_PATH)


@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})


@api.route('/predict', methods=['POST'])
def predict():
    try:
        if 'image' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No image file provided'
            }), 400

        file = request.files['image']
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

        predictions = detector.predict(img)

        return jsonify({
            'status': 'success',
            'predictions': predictions
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
