import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

from early.classifier.base import BaseClassifier


class SoftAttention(tf.keras.layers.Layer):
    def __init__(self, units, **kwargs):
        super(SoftAttention, self).__init__(**kwargs)
        self.units = units

    def build(self, input_shape):
        self.W1 = tf.keras.layers.Dense(self.units)
        self.V = tf.keras.layers.Dense(1)
        super(SoftAttention, self).build(input_shape)

    def call(self, features):
        attention_hidden_layer = (tf.nn.tanh(self.W1(features)))
        score = self.V(attention_hidden_layer)
        attention_weights = tf.nn.softmax(score, axis=-2)

        context_vector = attention_weights * features
        context_vector = tf.reduce_sum(context_vector, axis=1)
        return context_vector, attention_weights

    def get_config(self):
        config = super(SoftAttention, self).get_config()
        config.update({"units": self.units})
        return config


class EarlyClassifier(BaseClassifier):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = load_model(
            self.current_dir / "model_gru_fagor_tool_att_1003-164942_3.h5", compile=False,
            custom_objects={"SoftAttention": SoftAttention, }
        )
        self.max_header_size = 44
        self.max_payload_size = 500
        self.padding_position = "post"
        self.label_code = [
            "Normal",
            "Bruteforce",
            "Malformed",
            "SlowDoS",
        ]

    def get_confidence(self, score):
        return round(float(np.max(score)) * 100)

    def get_label(self, score):
        return self.label_code[np.argmax(score)]
