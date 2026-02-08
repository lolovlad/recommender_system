Вот обновлённая версия твоего README с учётом нового кода — `S3Storage` и `DataSyncService`, а также использования `.env` для конфигурации:

````markdown
# Recommender System (Lab 1)

Проект демонстрирует скелет ИИ-системы, реализованный по принципам Clean Architecture.

## Структура

- `domain` — сущности и интерфейсы
- `application` — бизнес-логика
- `infrastructure` — реализация модели (Mock) и хранилища данных (S3/MinIO)
- `presentation` — CLI-интерфейс и скрипт синхронизации данных

## Конфигурация

Создайте файл `.env` для конфигурации S3/MinIO:

```env
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=datasets
````

## Запуск рекомендательной системы

Для запуска CLI:

```bash
poetry install
poetry run python src/presentation/cli.py --user-id u1 --items itemA,itemB
```

CLI принимает аргументы:

* `--user-id` — идентификатор пользователя
* `--items` — список последних просмотренных пользователем элементов (через запятую)

## Синхронизация данных через S3/MinIO

Для скачивания данных из бакета S3/MinIO:

```bash
poetry run python src/main.py
```

Скрипт `main.py` использует:

1. `S3Storage` — реализация хранилища данных
2. `DataSyncService` — сервис для синхронизации файлов
3. Задаёт `remote_path` и `local_path` для скачивания файлов, например:

```python
sync_service.sync_dataset(
    remote_path="raw/reviews.csv",
    local_path="data/reviews.csv"
)
```

## Тестирование

Для запуска unit-тестов используется `pytest`:

```bash
poetry run pytest
```

Ты имеешь в виду **DVC (Data Version Control)**, чтобы управлять датасетами и синхронизацией через S3/MinIO? Я напишу набор базовых команд для твоего проекта.

---

### Инициализация DVC в проекте

```bash
# Инициализируем DVC
poetry run dvc init
```

Это создаст `.dvc/` и `.dvcignore`.

---

### Настройка удалённого хранилища (S3/MinIO)

```bash
poetry run dvc remote add -d myremote s3://datasets
poetry run dvc remote modify myremote endpointurl http://localhost:9000
poetry run dvc remote modify myremote access_key_id minioadmin
poetry run dvc remote modify myremote secret_access_key minioadmin
```

* `-d` делает этот remote **по умолчанию**.
* `myremote` — любое имя для удалённого хранилища.

---

### Добавление файлов/папок под контроль DVC

```bash
# Например, для датасета
poetry run dvc add data/reviews.csv
```

* Создаст файл `.dvc` (`reviews.csv.dvc`), который будет под Git.
* Сам файл `reviews.csv` останется локально, а DVC будет хранить его версию отдельно.

---

### Коммит в Git

```bash
git add data/reviews.csv.dvc .gitignore
git commit -m "Add dataset with DVC"
```

---

### Загрузка данных в удалённое хранилище

```bash
poetry run dvc push
```

* Отправляет файлы в S3/MinIO.
* Локально остаются файлы, а Git хранит только `.dvc` метаданные.

---

### Скачивание данных из удалённого хранилища

```bash
poetry run dvc pull
```

* Скачивает файлы, указанные в `.dvc` из `myremote`.
* Работает для новых членов команды или CI/CD.

---

### Проверка статуса DVC

```bash
poetry run dvc status
```

Запуск сервера
```bash
poetry run uvicorn src.presentation.api:app --reload
```

Swagger UI:

```bash
http://127.0.0.1:8000/docs
```

Создайте бакет models и зарегистрируйте его