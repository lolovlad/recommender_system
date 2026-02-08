from abc import ABC, abstractmethod
from .entities import UserHistory, Recommendation
import numpy as np


class Model(ABC):
    @abstractmethod
    def predict(self, input_data: np.ndarray) -> np.ndarray:
        pass


class ModelRecommend(ABC):
    @abstractmethod
    def recommend(self, user_id: int) -> list[int]:
        pass


class Recommender(ABC):

    @abstractmethod
    def get_recommendations(self, history: UserHistory) -> Recommendation:
        pass


class DataStorage(ABC):
   
    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> None:
        pass

    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> None:
        pass
