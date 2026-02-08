import os
from functools import lru_cache

from ..application.services import InferenceService
from ..application.recommendation_model_service import RecommendationService
from ..infrastructure.onnx_model import ONNXModel, ONNXRecommender


@lru_cache(maxsize=1)
def get_inference_service() -> InferenceService:
    model_path = "models/delivery_estimator.onnx"

    if not os.path.exists(model_path):
        raise RuntimeError("Модель не найдена. Выполните dvc pull")

    model = ONNXModel(model_path)
    return InferenceService(model)


@lru_cache
def get_recommendation_service() -> RecommendationService:
    model = ONNXRecommender(
        model_path="models/recommender.onnx",
        item_mapping_path="models/item_mapping.csv",
        user_item_matrix_path="models/user_item_matrix.csv",
        top_k=5
    )
    return RecommendationService(model)