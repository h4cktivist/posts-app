# posts-app

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%23D71F00.svg?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Pytest](https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3)

## Запуск через Docker

1. Скопируйте переменные окружения:

   ```bash
   cp .env.example .env
   ```

2. Поднимите сервисы:

   ```bash
   docker compose up --build
   ```

3. API: `http://localhost:8000`. Документация OpenAPI: `http://localhost:8000/docs`.

Стек в compose: приложение, PostgreSQL 15, Redis 7. Переменные `DATABASE_URL` и `REDIS_URL` в `.env` должны указывать на сервисы `db` и `redis` (как в `.env.example`).


## Тесты

Локально (Python 3.11+):

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests
```

Через Docker (без поднятия БД/Redis: интеграционные тесты используют SQLite в памяти):

```bash
docker compose build
docker compose run --rm --no-deps app python -m pytest tests
```

## Архитектура

<img width="1180" height="500" alt="Untitled Diagram drawio (19)" src="https://github.com/user-attachments/assets/9595077e-86fe-4474-9cb1-9037c93aad50" />

## Кеширование

Кэшируется только **один пост по числовому id** при обработке `GET /posts/{id}`. Создание поста кэш не заполняет: новая запись появится в Redis только после первого явного чтения по id (ленивое заполнение). При удалении или редактировании кэш инвалидируется. Также инвалидация происходит по истечении TTL.

Выбран подход **cache-aside**, так как нам достаточно ускорить **чтение по id**, а запись в кэш при мутациях не обязательна: достаточно сбросить ключ и дать кэшу заполниться при следующем чтении. Это позволяет хранить в кэше список только тех постов, которые наиболее часто запрашиваются пользователями, не перегружая его лишними данными.
