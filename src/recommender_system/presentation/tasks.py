from ..presentation.celery_app import celery_app
from ..presentation.dependencies import get_recommendation_service

service = get_recommendation_service()


@celery_app.task(name="generate_recommendations")
def generate_recommendations_task(user_id: int):
    items = service.generate(user_id)
    return {"items": items}