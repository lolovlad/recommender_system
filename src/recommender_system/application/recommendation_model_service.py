from ..domain.interfaces import Model


class RecommendationService:
    def __init__(self, model: Model):
        self.model = model

    def generate(self, user_id: int) -> list[int]:
        return self.model.recommend(user_id)