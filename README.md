# AnalyzeMate-Server

Репозиторий для сервера приложения для отображения списка ценных бумаг, 
их графиков текущих цен с возможностью отображения функций/метрик

# Локальный запуск

## Запуск в контейнере
1. Запускаем docker-compose:
```bash
docker-compose up --build
```

## Необходимо предварительно установить

- Создать виртуальное окружение для проекта, если необходимо
- `python 3.12`
- `pip install poetry`
- `pip install pre-commit`
- `poetry install`
- `pre-commit install`


## Настройки проекта
1. Директорию src пометить как `Sources Root`(Контекстное меню - `Mark Directory as` - `Sources Root`)