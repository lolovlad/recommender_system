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
)
EXPERIMENT_NAME = "Recommender System"
REGISTERED_MODEL_NAME = "recsys_model"

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

DVC_REMOTE = "myremote"


def ensure_active_experiment(experiment_name):
    client = MlflowClient()
    experiment = client.get_experiment_by_name(experiment_name)

    if experiment is None:
        mlflow.create_experiment(experiment_name)
        print(f"Создан новый эксперимент: {experiment_name}")
    elif experiment.lifecycle_stage == 'deleted':
        print(f"Эксперимент '{experiment_name}' находится в состоянии deleted. Удаляем окончательно...")
        client.delete_experiment(experiment.experiment_id)  # окончательное удаление
        mlflow.create_experiment(experiment_name)
        print(f"Создан новый эксперимент вместо удалённого: {experiment_name}")
    else:
        print(f"Эксперимент '{experiment_name}' активен.")


ensure_active_experiment(EXPERIMENT_NAME)


def train():
    if not os.path.exists(DATA_PATH):
        download_from_dvc(DATA_PATH, DATA_PATH, DVC_REMOTE)

    df = pd.read_csv(DATA_PATH)
    print(MLFLOW_TRACKING_URI)

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
            radius=None,
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

        mlflow.log_metric("ndcg_10", float(ndcg))

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
        print(f"NDCG_10: {ndcg:.4f}")


if __name__ == "__main__":
    train()
