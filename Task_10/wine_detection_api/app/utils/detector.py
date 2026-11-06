from ultralytics import YOLO


class WineDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.class_names = ['label', 'variety', 'vintage']

    def predict(self, image):
        results = self.model(image)
        predictions = []

        for r in results[0].boxes.data.tolist():
            x1, y1, x2, y2, conf, cls = r
            predictions.append({
                'class': int(cls),
                'class_name': self.class_names[int(cls)],
                'confidence': float(conf),
                'bbox': [float(x) for x in [x1, y1, x2, y2]]
            })

        return predictions
