from fastapi import FastAPI, Depends
import numpy as np

from ..domain.entities import DeliveryRequest, DeliveryResponse
from ..application.services import InferenceService
from ..presentation.dependencies import get_inference_service

app = FastAPI(title="Delivery Time Estimation API")

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
