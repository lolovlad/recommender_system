import mlflow


def check_ndcg():
    client = mlflow.tracking.MlflowClient()
    runs = client.search_runs(
        experiment_ids=["0"],
        order_by=["metrics.ndcg@10 DESC"],
        max_results=1
    )

    ndcg = runs[0].data.metrics["ndcg@10"]
    if ndcg <= 0.5:
        raise ValueError(f"NDCG@10 too low: {ndcg}")

    print("Quality gate passed:", ndcg)


if __name__ == "__main__":
    check_ndcg()