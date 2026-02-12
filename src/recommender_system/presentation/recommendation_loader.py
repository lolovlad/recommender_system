import os
import mlflow
from mlflow.tracking import MlflowClient

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI_DOCKER")
print(MLFLOW_TRACKING_URI)
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

MODEL_DIR = "models"
MODEL_NAME = "recsys_model"
STAGE = "Production"


def load_recsys_from_mlflow():
    os.makedirs(MODEL_DIR, exist_ok=True)

    client = MlflowClient()

    versions = client.get_latest_versions(MODEL_NAME)
    if not versions:
        raise RuntimeError("No Production model found in MLflow")

    model_version = versions[0]
    run_id = model_version.run_id

    model_path = client.download_artifacts(
        run_id,
        "model",
        MODEL_DIR
    )

    os.rename(
        os.path.join(model_path, "model.onnx"),
        os.path.join(MODEL_DIR, "recommender.onnx")
    )

    client.download_artifacts(run_id, "item_mapping.csv", MODEL_DIR)
    client.download_artifacts(run_id, "user_item_matrix.csv", MODEL_DIR)

    print("Recommender model loaded from MLflow")

