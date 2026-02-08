from fastapi import FastAPI, Depends
from celery.result import AsyncResult
import numpy as np

from ..domain.entities import DeliveryRequest, DeliveryResponse, RecommendationRequest
from ..application.services import InferenceService
from ..presentation.dependencies import get_inference_service
from ..presentation.tasks import generate_recommendations_task, celery_app


app = FastAPI(title="Async Recommendation API")


@app.post("/api/v1/delivery/estimate_time", response_model=DeliveryResponse)
def estimate_time(
    request: DeliveryRequest,
    service: InferenceService = Depends(get_inference_service)
):
    features = np.array([[
        request.distance_km,
        request.hour,
        request.day_of_week,
        request.items_count
    ]])

    minutes = service.predict(features)
    return DeliveryResponse(estimated_minutes=round(minutes, 2))


@app.post("/api/v1/recommendations/generate_for_user", status_code=202)
def generate_async(request: RecommendationRequest):
    task = generate_recommendations_task.delay(request.user_id)
    return {"task_id": task.id}


@app.get("/api/v1/recommendations/results/{task_id}")
def get_result(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if result.ready():
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.get()
        }
    return {"task_id": task_id, "status": result.status}
