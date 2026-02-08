import onnxruntime as ort
import numpy as np
from ..domain.interfaces import Model, ModelRecommend
import pandas as pd


class ONNXRecommender(ModelRecommend):
    def __init__(self,
                 model_path: str,
                 item_mapping_path: str,
                 user_item_matrix_path: str,
                 top_k: int = 5
                 ):
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name

        self.item_ids = pd.read_csv(item_mapping_path, header=None)[0].tolist()

        self.user_item_matrix = pd.read_csv(
            user_item_matrix_path,
            index_col=0
        )

        self.top_k = top_k

    def recommend(self, user_id: int) -> list[int]:
        if user_id not in self.user_item_matrix.index:
            return []

        user_vector = self.user_item_matrix.loc[user_id].values.astype(np.float32)
        user_vector = user_vector.reshape(1, -1)

        distances, indices = self.session.run(
            None,
            {self.input_name: user_vector}
        )

        recommended_item_indices = indices[0]

        recommendations = [
            self.item_ids[int(i)]
            for i in recommended_item_indices
            if 0 <= int(i) < len(self.item_ids)
        ]

        return recommendations


class ONNXModel(Model):
    def __init__(self, model_path: str):
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, input_data: np.ndarray) -> np.ndarray:
        input_data = input_data.astype(np.float32)
        result = self.session.run(None, {self.input_name: input_data})
        return result[0]