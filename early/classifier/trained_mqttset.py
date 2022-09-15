import numpy as np
from tensorflow.keras.models import load_model

from early.classifier.base import BaseClassifier


class EarlyClassifier(BaseClassifier):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = load_model(self.current_dir / "model_1dcnn_0109-145711_2.h5", compile=False)
        self.max_header_size = 50
        self.max_payload_size = 2000
        self.padding_position = "post"
        self.label_code = [
            "Normal",
            "Flood",
            "MalariaDoS",
            "Malformed",
            "Slowite",
            "Bruteforce"
        ]

    def get_confidence(self, score):
        return round(float(np.max(score)) * 100)

    def get_label(self, score):
        return self.label_code[np.argmax(score)]
