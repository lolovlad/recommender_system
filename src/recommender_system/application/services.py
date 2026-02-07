from pathlib import Path
from ..domain.interfaces import DataStorage

class DataSyncService:

    def __init__(self, storage: DataStorage):
        self.storage = storage

    def sync_dataset(self, remote_path: str, local_path: str) -> None:
        local_file = Path(local_path)
        if not local_file.exists():
            print(f"[Sync] Файл {local_path} не найден. Загружаю из облака...")
            local_file.parent.mkdir(parents=True, exist_ok=True)
            self.storage.download_file(remote_path, local_path)
        else:
            print(f"[Sync] Файл {local_path} уже существует. Пропускаю.")
