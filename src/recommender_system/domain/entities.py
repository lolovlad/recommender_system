from pydantic import BaseModel


class UserHistory(BaseModel):
    user_id: str
    last_items: list[str]


class Recommendation(BaseModel):
    suggested_items: list[str]
    engine_version: str


class DeliveryRequest(BaseModel):
    distance_km: float
    hour: int
    day_of_week: int
    items_count: int


class DeliveryResponse(BaseModel):
    estimated_minutes: float


class RecommendationRequest(BaseModel):
    user_id: int


class RecommendationResponse(BaseModel):
    items: list[int]

