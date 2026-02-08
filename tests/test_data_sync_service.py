import os
import tempfile
import pytest
from src.recommender_system.infrastructure.storage import S3Storage
from src.recommender_system.application.services import DataSyncService

class MockS3Storage(S3Storage):
    def __init__(self):
        self.files = {}

    def upload_file(self, local_path: str, remote_path: str):
        with open(local_path, "rb") as f:
            self.files[remote_path] = f.read()

    def download_file(self, remote_path: str, local_path: str):
        if remote_path not in self.files:
            raise FileNotFoundError(f"{remote_path} not found in mock S3")
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(self.files[remote_path])

@pytest.fixture
def mock_s3_storage():
    storage = MockS3Storage()
    test_content = b"user_id,item_id,rating\n1,101,5\n2,102,4\n"
    storage.files["raw/reviews.csv"] = test_content
    return storage

def test_sync_dataset(mock_s3_storage):
    with tempfile.TemporaryDirectory() as tmpdir:
        local_path = os.path.join(tmpdir, "reviews.csv")
        service = DataSyncService(storage=mock_s3_storage)

        service.sync_dataset(remote_path="raw/reviews.csv", local_path=local_path)

        assert os.path.exists(local_path)

        with open(local_path, "rb") as f:
            content = f.read()
        assert content == mock_s3_storage.files["raw/reviews.csv"]