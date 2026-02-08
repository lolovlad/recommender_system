import os
from functools import lru_cache

from ..application.services import InferenceService
from ..infrastructure.onnx_model import ONNXModel

@lru_cache(maxsize=1)
def get_inference_service() -> InferenceService:
    model_path = "models/delivery_estimator.onnx"

    if not os.path.exists(model_path):
        raise RuntimeError("Модель не найдена. Выполните dvc pull")

    model = ONNXModel(model_path)
    return InferenceService(model)