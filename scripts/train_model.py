import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

df = pd.read_csv("data/processed/deliveries.csv")

X = df[["distance_km", "hour", "day_of_week", "items_count"]].astype(np.float32)
y = df["delivery_minutes"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = GradientBoostingRegressor(random_state=42)
model.fit(X_train, y_train)

print("R2 score:", model.score(X_test, y_test))

initial_type = [("float_input", FloatTensorType([None, X.shape[1]]))]
onnx_model = convert_sklearn(model, initial_types=initial_type)

with open("models/delivery_estimator.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())

print("Модель сохранена в models/delivery_estimator.onnx")