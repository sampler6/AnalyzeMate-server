# AnalyzeMate-Server

Репозиторий для сервера приложения для отображения списка ценных бумаг, 
их графиков текущих цен с возможностью отображения функций/метрик

Приложения поддерживает регистрацию пользователей, отображения акций с биржи, составление личных портфелей и получения рекомендаций через уведомления на Android

frontend(Android): https://github.com/hestiates/AnalyzeMate

# Локальный запуск

## Необходимо предварительно установить

- Создать виртуальное окружение для проекта, если необходимо
- `python 3.12`
- `pip install poetry`
- `pip install pre-commit`
- `poetry install`
- `pre-commit install`
- Скопировать .env-non-dev в .env. Если необходимо, заполнить незаполненные параметры
TOKEN=#Токен TINKOFFAPI для получения данных с биржи
LOAD_SECURITIES=False  # Установить на True для работы приложения
FCM_KEY=KEY  # Ключ FCM для получения уведомлений на мобильные устройства

## Настройки проекта
1. Директорию src пометить как `Sources Root`(Контекстное меню - `Mark Directory as` - `Sources Root`)


## Запуск в контейнере
1. Запускаем docker-compose:
```bash
docker-compose up --build
```

Приложение будет доступно по адресу localhost:8000(swagger: localhost:8000/docs), а бд localhost:5433

# Запуск тестов

```bash
docker-compose up -d --build --wait; pytest -rfs -vv --color yes; docker-compose down
```

# git commit
В проекте используется pre-commit. Каждый коммит проходит проверку линтерами.
Линтеры запускаются автоматически при коммите. Если хотите запустить их сами:
- `pre-commit run --all-files`

# alembic
Для работы с alembic необходимо перейти в папку src:

```bash
cd src
```

И поменять в .env DB_HOST=db -> DB_HOST=localhost
