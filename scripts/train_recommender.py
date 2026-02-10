import pandas as pd
import os

from sklearn.neighbors import NearestNeighbors
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# Пути
DATA_PATH = "data/processed/interactions.csv"
MODEL_PATH = "models/recommender.onnx"

df = pd.read_csv(DATA_PATH)

user_item_matrix = df.pivot_table(
    index="user_id",
    columns="item_id",
    values="rating",
    fill_value=0
)

model = NearestNeighbors(
    n_neighbors=5,
    radius=None,
    metric="cosine",
    algorithm = "brute"
)

model.fit(user_item_matrix.values)

initial_type = [
    ("float_input", FloatTensorType([None, user_item_matrix.shape[1]]))
]

onnx_model = convert_sklearn(
    model,
    initial_types=initial_type
)

os.makedirs("models", exist_ok=True)

with open(MODEL_PATH, "wb") as f:
    f.write(onnx_model.SerializeToString())

item_mapping = {
    "items": list(user_item_matrix.columns)
}

pd.Series(item_mapping["items"]).to_csv(
    "models/item_mapping.csv",
    index=False
)

user_item_matrix.to_csv("models/user_item_matrix.csv")

print("Модель рекомендаций сохранена")
print(f"Users: {user_item_matrix.shape[0]}")
print(f"Items: {user_item_matrix.shape[1]}")