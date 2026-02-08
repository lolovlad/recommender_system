from minio import Minio
from ..domain.interfaces import DataStorage


class S3Storage(DataStorage):

    def __init__(self, 
                 endpoint_url: str, 
                 access_key: str, 
                 secret_key: str, 
                 bucket: str):
        
        self.bucket = bucket
        self.client = Minio(
            endpoint=endpoint_url,
            access_key=access_key,
            secret_key=secret_key,
            secure=False 
        )
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)

    def download_file(self, remote_path: str, local_path: str) -> None:
        print(f"[Storage] Скачивание {remote_path} → {local_path}...")
        self.client.fget_object(self.bucket, remote_path, local_path)

    def upload_file(self, local_path: str, remote_path: str) -> None:
        print(f"[Storage] Загрузка {local_path} → {remote_path}...")
        self.client.fput_object(self.bucket, remote_path, local_path)
