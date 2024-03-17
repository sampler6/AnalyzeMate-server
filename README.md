# AnalyzeMate-Server

Репозиторий для сервера приложения для отображения списка ценных бумаг, 
их графиков текущих цен с возможностью отображения функций/метрик

# Локальный запуск

## Необходимо предварительно установить

- Создать виртуальное окружение для проекта, если необходимо
- `python 3.12`
- `pip install poetry`
- `pip install pre-commit`
- `poetry install`
- `pre-commit install`
- Скопировать .env-non-dev в .env. Если необходимо, заполнить незаполненные параметры

## Настройки проекта
1. Директорию src пометить как `Sources Root`(Контекстное меню - `Mark Directory as` - `Sources Root`)


## Запуск в контейнере
1. Запускаем docker-compose:
```bash
docker-compose up --build
```

Приложение будет доступно по адресу localhost:8000(swagger: localhost:8000/docs), а бд localhost:5433

## Тест на запуск приложения

```bash
docker-compose -f docker-compose.test.yml up --build
```

## git commit
В проекте используется pre-commit. Каждый коммит проходит проверку линтерами.
Линтеры запускаются автоматически при коммите. Если хотите запустить их сами:
- `pre-commit run --all-files`
