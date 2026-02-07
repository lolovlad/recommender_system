import argparse
import os
from dotenv import load_dotenv
from ..domain.entities import UserHistory
from ..infrastructure.collaborative import CollaborativeMockModel
from ..application.recommendation_service import RecommendationService
from ..application.services import DataSyncService
from ..infrastructure.storage import S3Storage

def main():
    load_dotenv()

    host = os.getenv("MINIO_HOST")
    port = os.getenv("MINIO_PORT")
    access_key = os.getenv("MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY")
    bucket = os.getenv("MINIO_BUCKET")


    parser = argparse.ArgumentParser(description="Recommender System CLI")
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--items", default="")

    args = parser.parse_args()
    items = args.items.split(",") if args.items else []

    history = UserHistory(
        user_id=args.user_id,
        last_items=items
    )

    model = CollaborativeMockModel()
    service = RecommendationService(model)

    storage = S3Storage(f"{host}:{port}", access_key, secret_key, bucket)
    sync_service = DataSyncService(storage=storage)

    recommendation = service.get_recommendations(history)

    sync_service.sync_dataset(
        remote_path="raw/reviews.csv",
        local_path="data/reviews.csv"
    )



    for idx, item in enumerate(recommendation.suggested_items, 1):
        print(f"{idx}. {item}")


if __name__ == "__main__":
    main()