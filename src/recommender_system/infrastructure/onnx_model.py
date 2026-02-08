import onnxruntime as ort
import numpy as np
from ..domain.interfaces import Model


class ONNXModel(Model):
    def __init__(self, model_path: str):
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, input_data: np.ndarray) -> np.ndarray:
        input_data = input_data.astype(np.float32)
        result = self.session.run(None, {self.input_name: input_data})
        return result[0]