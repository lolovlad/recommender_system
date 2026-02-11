import os
import pandas as pd

import mlflow
import mlflow.onnx

from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import ndcg_score
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import dvc.api


DATA_PATH = "data/processed/interactions.csv"

MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000"
)

EXPERIMENT_NAME = "Recommender System"
REGISTERED_MODEL_NAME = "recsys_model"

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

DVC_REMOTE = "myremote"


def download_from_dvc(dvc_path: str, local_path: str, remote_name: str = None):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    try:
        print(f"Скачиваем {dvc_path} через DVC API...")

        with dvc.api.open(
            path=dvc_path,
            repo=".",           # текущий репозиторий
            remote=remote_name, # remote из config
            mode="rb"
        ) as fd, open(local_path, "wb") as out:
            out.write(fd.read())

        print("Файл успешно скачан через DVC.")

    except Exception as e:
        print("Ошибка при скачивании через DVC:", e)
        raise


def train():
    if not os.path.exists(DATA_PATH):
        download_from_dvc(DATA_PATH, DATA_PATH, DVC_REMOTE)

    df = pd.read_csv(DATA_PATH)

    user_item_matrix = df.pivot_table(
        index="user_id",
        columns="item_id",
        values="rating",
        fill_value=0
    )

    X = user_item_matrix.values

    n_neighbors = 5
    metric = "cosine"
    algorithm = "brute"

    with mlflow.start_run():
        mlflow.log_param("n_neighbors", n_neighbors)
        mlflow.log_param("metric", metric)
        mlflow.log_param("algorithm", algorithm)
        mlflow.log_param("users_count", user_item_matrix.shape[0])
        mlflow.log_param("items_count", user_item_matrix.shape[1])

        model = NearestNeighbors(
            n_neighbors=n_neighbors,
            metric=metric,
            algorithm=algorithm
        )

        model.fit(X)

        k = min(10, X.shape[0])
        X_test = X[:k]

        distances, indices = model.kneighbors(X_test)

        y_true = X_test
        y_score = X[indices[:, 0]]

        ndcg = ndcg_score(y_true, y_score, k=10)

        mlflow.log_metric("ndcg@10", float(ndcg))

        initial_type = [
            ("float_input", FloatTensorType([None, X.shape[1]]))
        ]

        onnx_model = convert_sklearn(
            model,
            initial_types=initial_type
        )

        mlflow.onnx.log_model(
            onnx_model,
            artifact_path="model",
            registered_model_name=REGISTERED_MODEL_NAME
        )

        user_item_matrix.to_csv("user_item_matrix.csv")
        pd.Series(user_item_matrix.columns).to_csv(
            "item_mapping.csv",
            index=False
        )

        mlflow.log_artifact("user_item_matrix.csv")
        mlflow.log_artifact("item_mapping.csv")

        print("Модель рекомендаций успешно обучена и сохранена в MLflow")
        print(f"Users: {user_item_matrix.shape[0]}")
        print(f"Items: {user_item_matrix.shape[1]}")
        print(f"NDCG@10: {ndcg:.4f}")


if __name__ == "__main__":
    train()
